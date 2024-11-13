from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.services.admin_charts_api_functions import (
    get_entity_breakdown_counts, get_evince_status_counts,
    get_inspector_activity_metrics, get_model_counts, statistic_cards_data)
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

    @action(detail=False, methods=["get"], url_path="overall_counts")
    def overall_counts(self, request):

        data = statistic_cards_data()
        return Response(data)

    @action(detail=False, methods=["get"], url_path="evince_status_counts")
    def evince_status_counts(self, request):
        time_period = request.query_params.get("time_period", "all")
        end_date = now()
        if time_period.isdigit():
            start_date = end_date - timedelta(days=int(time_period))
        elif time_period == "week":
            start_date = end_date - timedelta(days=7)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = None

        queryset = Evince.objects.all()
        if start_date:
            queryset = queryset.filter(
                changed_on__gte=start_date, changed_on__lte=end_date
            )
        evince_status_counts = queryset.values("status").annotate(count=Count("id"))
        status_counts = {
            entry["status"]: entry["count"] for entry in evince_status_counts
        }
        all_statuses = ["Approved", "Rejected", "ResultsEntered", "Logged"]
        for status in all_statuses:
            status_counts.setdefault(status, 0)
        total_evinces = sum(status_counts.values())
        status_counts["total_evinces"] = total_evinces

        return Response(status_counts)

    @action(detail=False, methods=["get"], url_path="inspection_progress_summary")
    def inspection_progress_summary(self, request):
        inspection_counts = Evince.objects.values("status").annotate(count=Count("id"))
        total_inspections = Evince.objects.count()
        data = {
            "total_inspections": total_inspections,
            "status_counts": {
                item["status"]: item["count"] for item in inspection_counts
            },
        }
        return Response(data)

    @action(detail=False, methods=["get"], url_path="evince_status_overview")
    def evince_status_overview(self, request):
        time_period = request.query_params.get("time_period", "all")
        end_date = now()

        if time_period == "Today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            last_start_date = start_date - timedelta(days=1)
            last_end_date = start_date
        elif time_period == "week":
            start_date = end_date - timedelta(days=7)
            last_start_date = start_date - timedelta(days=7)
            last_end_date = start_date
        elif time_period == "last_week":
            start_date = end_date - timedelta(days=14)
            last_start_date = start_date - timedelta(days=7)
            last_end_date = start_date
        else:
            start_date = None
            last_start_date = None
            last_end_date = None
        queryset = Evince.objects.all()
        if start_date:
            current_period_queryset = queryset.filter(
                changed_on__gte=start_date, changed_on__lte=end_date
            )
        else:
            current_period_queryset = queryset
        if last_start_date and last_end_date:
            last_period_queryset = queryset.filter(
                changed_on__gte=last_start_date, changed_on__lt=last_end_date
            )
        else:
            last_period_queryset = queryset.none()
        current_status_counts = current_period_queryset.values("status").annotate(
            count=Count("id")
        )
        current_counts = {
            entry["status"]: entry["count"] for entry in current_status_counts
        }
        last_status_counts = last_period_queryset.values("status").annotate(
            count=Count("id")
        )
        last_counts = {entry["status"]: entry["count"] for entry in last_status_counts}
        all_statuses = [
            "Approved",
            "Rejected",
            "ResultsEntered",
            "Logged",
            "Reassigned",
            "Completed",
        ]
        status_comparison = {}
        for status in all_statuses:
            current_count = current_counts.get(status, 0)
            last_count = last_counts.get(status, 0)
            comparison = current_count - last_count
            status_comparison[status] = {
                "count": current_count,
                "comparison_to_last_week": comparison,
            }
        total_evinces = sum(current_counts.values())
        response_data = {
            "total_evinces": total_evinces,
            "status_counts": status_comparison,
        }

        return Response(response_data)

    @action(detail=False, methods=["get"], url_path="top_managers")
    def top_managers(self, request):
        time_period = request.query_params.get("time_period", "all")
        end_date = now()
        if time_period == "week":
            start_date = end_date - timedelta(days=7)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = None
        queryset = Evince.objects.filter(status="Approved", reviewed_by__isnull=False)
        if start_date:
            queryset = queryset.filter(
                changed_on__gte=start_date, changed_on__lte=end_date
            )
        manager_approval_counts = (
            queryset.values(
                "reviewed_by__id", "reviewed_by__username", "reviewed_by__email"
            )
            .annotate(approved_count=Count("id"))
            .order_by("-approved_count")[:5]
        )

        response_data = [
            {
                "manager_id": item["reviewed_by__id"],
                "manager_name": item["reviewed_by__username"],
                "manager_email": item["reviewed_by__email"],
                "approved_count": item["approved_count"],
            }
            for item in manager_approval_counts
        ]

        return Response(response_data)

    @action(
        detail=False, methods=["get"], url_path="top_business_units_by_evince_count"
    )
    def top_business_units_by_evince_count(self, request):
        evince_counts = (
            Evince.objects.values("business_unit__name")
            .annotate(evince_count=Count("id"))
            .order_by("-evince_count")[:5]
        )

        response_data = [
            {
                "business_unit_name": item["business_unit__name"],
                "evince_count": item["evince_count"],
            }
            for item in evince_counts
        ]

        return Response(response_data)
