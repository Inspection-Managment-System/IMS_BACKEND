from django.contrib.auth.models import Group
from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from api.services.inspector_dashboard import (get_assigned_evinces,
                                              get_average_inspection_time,
                                              get_evinces_distribution,
                                              get_evinces_summary_with_details,
                                              get_inspection_status_breakdown,
                                              get_inspection_timeline,
                                              get_inspections_completed_today,
                                              get_overdue_inspections,
                                              get_pending_inspections,
                                              get_performance_trend,
                                              get_risk_levels,
                                              get_top_overdue_business_units)
from users.models import User, UserProfile


class InspectorDashboardViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["get"], url_path="assigned_evinces")
    def assigned_evinces(self, request):
        user = request.query_params.get("user")
        inspector_role = Group.objects.get(name="Inspector")
        user_profile = UserProfile.objects.filter(
            user=user, role=inspector_role
        ).first()
        if not user_profile:
            return Response(
                {"error": "User does not have inspector permissions"}, status=403
            )
        data = get_assigned_evinces(user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="inspection_status_breakdown")
    def inspection_status_breakdown(self, request):
        user = request.query_params.get("user")
        data = get_inspection_status_breakdown(user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="completed_today")
    def completed_today(self, request):
        user = request.query_params.get("user")
        data = get_inspections_completed_today(user)
        return Response({"completed_today": data})

    @action(detail=False, methods=["get"], url_path="pending_inspections")
    def pending_inspections(self, request):

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        user = request.query_params.get("user")
        data = get_pending_inspections(user, start_date=start_date, end_date=end_date)
        return Response({"pending_inspections": data})

    @action(detail=False, methods=["get"], url_path="overdue_inspections")
    def overdue_inspections(self, request):

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        user = request.query_params.get("user")
        data = get_overdue_inspections(user, start_date=start_date, end_date=end_date)
        return Response({"overdue_inspections": data})

    @action(detail=False, methods=["get"], url_path="average_inspection_time")
    def average_inspection_time(self, request):
        user = request.query_params.get("user")
        data = get_average_inspection_time(user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="evinces_distribution")
    def evinces_distribution(self, request):
        user = request.query_params.get("user")
        data = get_evinces_distribution(user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="inspection_timeline")
    def inspection_timeline(self, request):
        user = request.query_params.get("user")
        data = get_inspection_timeline(user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="performance_trend")
    def performance_trend(self, request):
        user = request.query_params.get("user")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        data = get_performance_trend(user, start_date=start_date, end_date=end_date)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="risk_levels")
    def risk_levels(self, request):
        user = request.query_params.get("user")
        data = get_risk_levels(user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="top_overdue_business_units")
    def top_overdue_business_units(self, request):
        """
        Fetch the top overdue business units based on the evince count, filtered by user and date range.
        """
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        user_id = request.query_params.get("user")
        limit = int(request.query_params.get("limit", 5))

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound({"error": f"User with ID {user_id} does not exist."})

        data = get_top_overdue_business_units(
            user=user,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return Response({"top_overdue_business_units": data})

    @action(
        detail=False, methods=["get"], url_path="assigned_evinces_summary_with_details"
    )
    def assigned_evinces_summary_with_details(self, request):
        user = request.query_params.get("user")
        if not user:
            return Response(
                {"error": "Inspector not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        summary = get_evinces_summary_with_details(user)
        return Response(summary, status=status.HTTP_200_OK)
