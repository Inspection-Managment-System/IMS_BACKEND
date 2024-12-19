from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import now

from inspection_management.models import DataGroup, Evince


def get_evince_status_overview(user_id, time_period):
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

    data_groups = DataGroup.objects.filter(user_profiles__user_id=user_id)
    queryset = (
        Evince.objects.filter(business_unit__group__in=data_groups)
        if data_groups.exists()
        else Evince.objects.none()
    )

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
    last_status_counts = last_period_queryset.values("status").annotate(
        count=Count("id")
    )

    current_counts = {
        entry["status"]: entry["count"] for entry in current_status_counts
    }
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

    return response_data
