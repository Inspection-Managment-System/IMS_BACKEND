from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.services.inspector_dashboard import (get_assigned_evinces,
                                              get_average_inspection_time,
                                              get_evinces_distribution,
                                              get_inspection_status_breakdown,
                                              get_inspection_timeline,
                                              get_inspections_completed_today,
                                              get_overdue_inspections,
                                              get_pending_inspections,
                                              get_performance_trend,
                                              get_risk_levels)
from users.models import UserProfile


class InspectorDashboardViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["get"], url_path="assigned_evinces")
    def assigned_evinces(self, request):
        inspector_role = Group.objects.get(name="Inspector")
        user_profile = UserProfile.objects.filter(
            user=request.user, role=inspector_role
        ).first()
        if not user_profile:
            return Response(
                {"error": "User does not have inspector permissions"}, status=403
            )
        data = get_assigned_evinces(request.user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="inspection_status_breakdown")
    def inspection_status_breakdown(self, request):
        inspector = request.user
        data = get_inspection_status_breakdown(inspector)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="completed_today")
    def completed_today(self, request):
        data = get_inspections_completed_today(request.user)
        return Response({"completed_today": data})

    @action(detail=False, methods=["get"], url_path="pending_inspections")
    def pending_inspections(self, request):
        data = get_pending_inspections(request.user)
        return Response({"pending_inspections": data})

    @action(detail=False, methods=["get"], url_path="overdue_inspections")
    def overdue_inspections(self, request):
        data = get_overdue_inspections(request.user)
        return Response({"overdue_inspections": data})

    @action(detail=False, methods=["get"], url_path="average_inspection_time")
    def average_inspection_time(self, request):
        data = get_average_inspection_time(request.user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="evinces_distribution")
    def evinces_distribution(self, request):
        data = get_evinces_distribution(request.user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="inspection_timeline")
    def inspection_timeline(self, request):
        data = get_inspection_timeline(request.user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="performance_trend")
    def performance_trend(self, request):
        data = get_performance_trend(request.user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="risk_levels")
    def risk_levels(self, request):
        data = get_risk_levels(request.user)
        return Response(data)
