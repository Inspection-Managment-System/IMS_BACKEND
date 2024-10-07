from datetime import timedelta

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import EvinceSerializer
from ims_backend.utils.helper import get_user_groups
from inspection_management.models import (BusinessUnit, Evince,
                                          InspectionAnalysis, InspectionPoint,
                                          InspectionResult, InspectionTest)
from users.authorization import role_required


@method_decorator(role_required(allowed_roles=["Admin", "Manager"]), name="dispatch")
class EvinceViewSet(viewsets.ModelViewSet):
    queryset = Evince.objects.all()
    serializer_class = EvinceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id", None)
        business_unit = request.query_params.get("business_unit", None)
        inspection_point = request.query_params.get("inspection_point", None)
        analysis_type = request.query_params.get("analysis_type", None)
        number_of_days = request.query_params.get("number_of_days", None)
        status = request.query_params.get("status", None)
        count = request.query_params.get("count", None)
        managed_by = request.query_params.get("managed_by", None)

        filters = Q()

        if user_id:
            user_data_groups_ids = get_user_groups(user_id)
            if user_data_groups_ids:
                filters &= Q(inspection_point__group__id__in=user_data_groups_ids)
        if business_unit:
            filters &= Q(business_unit__name=business_unit)
        if inspection_point:
            filters &= Q(inspection_point__name=inspection_point)
        if analysis_type:
            filters &= Q(inspection_analyses__analysis_type__name=analysis_type)
        if number_of_days:
            target_date = now() - timedelta(days=int(number_of_days))
            filters &= Q(start_date_time__gte=target_date)
        if status:
            filters &= Q(status=status)
        if managed_by:
            filters &= Q(reviewed_by__username=managed_by)

        filtered_queryset = (
            self.queryset.filter(filters).distinct() if filters else self.queryset.all()
        )

        if count and count.lower() == "true":
            response_data = []
            status_labels = Evince.get_status_labels()

            for key, value in status_labels.items():
                evinces_count = filtered_queryset.filter(status=key).count()
                response_data.append(
                    {"value": value, "label": value, "count": evinces_count}
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
        self.create_inspection_tests_and_results(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def create_inspection_tests_and_results(self, evince):
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
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

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
