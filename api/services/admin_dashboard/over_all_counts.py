from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import now

from inspection_management.models import DataGroup, Evince


def get_evince_status_counts(user_id, time_period):
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

    data_groups = DataGroup.objects.filter(user_profiles__user_id=user_id)

    queryset = (
        Evince.objects.filter(business_unit__group__in=data_groups)
        if data_groups.exists()
        else Evince.objects.none()
    )

    if start_date:
        queryset = queryset.filter(changed_on__gte=start_date, changed_on__lte=end_date)

    evince_status_counts = queryset.values("status").annotate(count=Count("id"))

    status_counts = {entry["status"]: entry["count"] for entry in evince_status_counts}

    all_statuses = ["Approved", "Rejected", "ResultsEntered", "Logged"]
    for status in all_statuses:
        status_counts.setdefault(status, 0)

    total_evinces = sum(status_counts.values())
    status_counts["total_evinces"] = total_evinces

    return status_counts
