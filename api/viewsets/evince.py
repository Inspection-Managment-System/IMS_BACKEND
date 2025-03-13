from datetime import timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (EvinceSerializer, ParameterSerializer,
                             SimplifiedInspectionResultSerializer)
from ims_backend.utils.helper import get_user_groups
from inspection_management.models import (BusinessUnit, Evince,
                                          InspectionAnalysis, InspectionPoint,
                                          InspectionResult, InspectionTest,
                                          Parameter)
from users.authorization import role_required
from users.models import User
from users.models.audit_history import AuditHistory
from users.models.notification import Notification


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class EvinceViewSet(viewsets.ModelViewSet):
    queryset = Evince.objects.all().order_by("-id")
    serializer_class = EvinceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id", None)
        business_unit = request.query_params.get("business_unit", None)
        site = request.query_params.get("site", None)
        inspection_point = request.query_params.get("inspection_point", None)
        analysis_type = request.query_params.get("analysis_type", None)
        number_of_days = request.query_params.get("number_of_days", None)
        status = request.query_params.get("status", None)
        count = request.query_params.get("count", None)
        managed_by = request.query_params.get("managed_by", None)
        inspected_by = request.query_params.get("inspected_by", None)

        filters = Q()

        if user_id:
            user_data_groups_ids = get_user_groups(user_id)
            if user_data_groups_ids:
                filters &= Q(inspection_point__group__id__in=user_data_groups_ids)
        if site:
            filters &= Q(business_unit__site__name=site)

        if business_unit:
            filters &= Q(business_unit__name=business_unit)

        if inspection_point:
            filters &= Q(inspection_point__name=inspection_point)
        if analysis_type:
            filters &= Q(inspection_analyses__analysis_type__name=analysis_type)
        if number_of_days:
            if number_of_days and number_of_days.isdigit():
                days = int(number_of_days)
                target_date = now() - timedelta(days=days)
                filters &= Q(start_date_time__gte=target_date)
        if status:
            filters &= Q(status=status)
        if managed_by:
            filters &= Q(reviewed_by__username=managed_by)
        if inspected_by:
            filters &= Q(assigned_to__username=inspected_by)

        user = User.objects.get(id=user_id)
        user_profile = user.userprofile
        if user_profile.role.name == "Manager":
            filters &= Q(reviewed_by=user)
        elif user_profile.role.name == "Inspector":
            filters &= Q(assigned_to=user)

        filtered_queryset = (
            self.queryset.filter(filters).distinct() if filters else self.queryset.all()
        )

        if count and count.lower() == "true":
            response_data = {"statuses": [], "dayscount": []}

            status_labels = Evince.get_status_labels()
            for key, value in status_labels.items():
                evinces_count = filtered_queryset.filter(status=key).count()
                response_data["statuses"].append(
                    {"value": value, "label": value, "count": evinces_count}
                )
            time_ranges = [
                {"value": "All time", "label": "All time", "days": None},
                {"value": "5", "label": "Last 5 days", "days": 5},
                {"value": "10", "label": "Last 10 days", "days": 10},
                {"value": "15", "label": "Last 15 days", "days": 15},
                {"value": "30", "label": "Last month", "days": 30},
            ]

            for time_range in time_ranges:
                if time_range["days"] is not None:
                    time_threshold = timezone.now() - timedelta(days=time_range["days"])
                    days_count_queryset = filtered_queryset.filter(
                        start_date_time__gte=time_threshold
                    )
                    days_count = days_count_queryset.count()
                    print(
                        f"Count for {time_range['label']} ({time_range['days']} days): {days_count}"
                    )
                else:
                    days_count = filtered_queryset.count()
                    print(f"Count for All time: {days_count}")

                response_data["dayscount"].append(
                    {
                        "value": time_range["value"],
                        "label": time_range["label"],
                        "count": days_count,
                    }
                )

            return Response(response_data)

        self.queryset = filtered_queryset
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer.instance.save()
        self.create_inspection_tests_and_results(serializer.instance, is_update=False)

        AuditHistory.objects.create(
            user=request.user, action=f"Created evince #{serializer.instance.id}"
        )

        if (
            serializer.instance.assigned_to
            and serializer.instance.assigned_to != request.user
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.assigned_to,
                content=f"You have been assigned to evince #{serializer.instance.id}.",
            )

        if (
            serializer.instance.reviewed_by
            and serializer.instance.reviewed_by != request.user
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.reviewed_by,
                content=f"You have been assigned as reviewer for evince #{serializer.instance.id}.",
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def create_inspection_tests_and_results(self, evince, is_update=False):
        if is_update:
            InspectionTest.objects.filter(evince=evince).delete()
            InspectionResult.objects.filter(evince=evince).delete()
        for inspection_analysis in evince.inspection_analyses.all():
            inspection_test = InspectionTest.objects.create(
                evince=evince,
                inspection_analysis=inspection_analysis,
                changed_by=evince.changed_by,
            )
            InspectionResult.objects.create(
                evince=evince,
                inspection_test=inspection_test,
                changed_by=evince.changed_by,
            )

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        original_assigned_to = instance.assigned_to
        original_reviewed_by = instance.reviewed_by
        original_status = instance.status

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.create_inspection_tests_and_results(serializer.instance, is_update=True)

        AuditHistory.objects.create(
            user=request.user, action=f"Updated evince #{serializer.instance.id}"
        )

        if (
            original_assigned_to != serializer.instance.assigned_to
            and serializer.instance.assigned_to
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.assigned_to,
                content=f"You have been assigned to evince #{serializer.instance.id}.",
            )

        if (
            original_reviewed_by != serializer.instance.reviewed_by
            and serializer.instance.reviewed_by
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.reviewed_by,
                content=f"You have been assigned as reviewer for evince #{serializer.instance.id}.",
            )

        return Response(serializer.data)

    def perform_destroy(self, instance):
        evince_id = instance.id

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted evince #{evince_id}"
        )

        if instance.assigned_to and instance.assigned_to != self.request.user:
            Notification.objects.create(
                sender=self.request.user,
                recipient=instance.assigned_to,
                content=f"Evince #{evince_id} that was assigned to you has been deleted.",
            )

        if instance.reviewed_by and instance.reviewed_by != self.request.user:
            Notification.objects.create(
                sender=self.request.user,
                recipient=instance.reviewed_by,
                content=f"Evince #{evince_id} that you were reviewing has been deleted.",
            )

        instance.delete()

    def preprocess_data(self, data):
        if "business_unit" in data:
            business_unit_name = data.get("business_unit")
            data["business_unit"] = BusinessUnit.objects.get(name=business_unit_name).id
        if "inspection_point" in data:
            inspection_point_name = data.get("inspection_point")
            data["inspection_point"] = InspectionPoint.objects.get(
                name=inspection_point_name
            ).id
        if "inspection_analyses" in data:
            inspection_analysis_names = data.get("inspection_analyses")
            for index, inspection_analysis_name in enumerate(inspection_analysis_names):
                data["inspection_analyses"][index] = InspectionAnalysis.objects.get(
                    name=inspection_analysis_name
                ).id
        return data

    @action(detail=True, methods=["get"], url_path="results")
    def get_results(self, request, pk=None):
        """
        Fetch the results and related parameters for a specific Evince.
        """
        inspection_results = InspectionResult.objects.filter(evince_id=pk)
        related_tests = InspectionTest.objects.filter(evince_id=pk).select_related(
            "inspection_analysis"
        )

        related_parameters = Parameter.objects.filter(
            inspection_analysis__inspectiontest__in=related_tests
        ).distinct()

        result_serializer = SimplifiedInspectionResultSerializer(
            inspection_results, many=True
        )
        parameter_serializer = ParameterSerializer(related_parameters, many=True)

        return Response(
            {
                "inspection_results": result_serializer.data,
                "related_parameters": parameter_serializer.data,
            }
        )

    @action(detail=True, methods=["post"], url_path="status-update")
    def update_status(self, request, pk=None):
        """
        API to update the status of the Evince based on the provided status and update InspectionResult data.
        """
        evince = get_object_or_404(Evince, pk=pk)
        old_status = evince.status
        status_to_update = request.data.get("status")

        if not status_to_update:
            return Response(
                {"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        evince.status = status_to_update

        self.handle_status_update(evince, status_to_update)

        evince.reassigned = True
        evince.save()

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated evince #{evince.id} status from {old_status} to {status_to_update}",
        )

        self.send_status_update_notifications(
            evince, old_status, status_to_update, request.user
        )

        return Response(
            {"message": f"Evince status updated to {status_to_update}."},
            status=status.HTTP_200_OK,
        )

    def send_status_update_notifications(self, evince, old_status, new_status, user):

        if new_status == "ResultsEntered":
            if evince.reviewed_by and evince.reviewed_by != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.reviewed_by,
                    content=f"Results have been entered for evince #{evince.id} and are ready for your review.",
                )

        elif new_status == "Rejected":
            if evince.assigned_to and evince.assigned_to != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.assigned_to,
                    content=f"Evince #{evince.id} has been rejected and requires your attention.",
                )

        elif new_status == "Reassigned":
            if evince.assigned_to and evince.assigned_to != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.assigned_to,
                    content=f"Evince #{evince.id} has been reassigned to you and requires your attention.",
                )

        elif new_status == "Approved":
            if evince.assigned_to and evince.assigned_to != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.assigned_to,
                    content=f"Evince #{evince.id} has been approved. Good job!",
                )

    def handle_status_update(self, evince, status_to_update):
        """
        Handles the status update and relevant InspectionResult modifications.
        """
        if status_to_update == "ResultsEntered":
            self.set_results_entered(evince)
        elif status_to_update == "Rejected":
            self.set_rejected(evince)
        elif status_to_update == "Reassigned":
            self.set_reassigned(evince)
        elif status_to_update == "Approved":
            self.set_approved(evince)

    def set_results_entered(self, evince):
        InspectionResult.objects.filter(evince=evince).update(status="Completed")

    def set_rejected(self, evince):
        pass

    def set_reassigned(self, evince):
        inspection_test_results = InspectionResult.objects.filter(evince=evince)
        for result in inspection_test_results:
            result.previous_value = result.entered_value
            result.status = "Incomplete"
            result.save()

    def set_approved(self, evince):
        pass
