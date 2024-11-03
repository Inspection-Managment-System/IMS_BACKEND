from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.services.detailed_entity_records import (
    get_entity_breakdown_counts, get_inspector_activity_metrics,
    get_model_counts)
from inspection_management.models import Evince


class AdminChartsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="detailed_entity_records")
    def fetch_detailed_records(self, request):
        data = get_model_counts()
        return Response(data)

    @action(detail=False, methods=["get"], url_path="another_function")
    def another_function(self, request):
        data = {"message": "Another function called."}
        return Response(data)

    @action(detail=False, methods=["get"], url_path="evince_management_overview")
    def evince_management_overview(self, request):
        time_period = request.query_params.get("days", 30)
        end_date = now()
        start_date = end_date - timedelta(days=int(time_period))
        user = request.user
        evince_data = (
            Evince.objects.filter(
                changed_on__range=[start_date, end_date], changed_by=user
            )
            .values("changed_on__date", "status")
            .annotate(count=Count("id"))
            .order_by("changed_on__date", "status")
        )
        response_data = {}
        for entry in evince_data:
            date = entry["changed_on__date"].strftime("%Y-%m-%d")
            status = entry["status"]
            count = entry["count"]
            if date not in response_data:
                response_data[date] = {}
            response_data[date][status] = count

        return Response(response_data)

    @action(detail=False, methods=["get"], url_path="entity_breakdown")
    def entity_breakdown(self, request):
        data = get_entity_breakdown_counts(request.user)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="inspector_activity_metrics")
    def inspector_activity_metrics(self, request):
        user_id = request.query_params.get("user_id")
        data = get_inspector_activity_metrics(user_id=user_id)
        return Response(data)
