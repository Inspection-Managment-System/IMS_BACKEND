from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import now

from inspection_management.models import Evince


def get_top_managers(time_period, limit=5):

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
        queryset = queryset.filter(changed_on__gte=start_date, changed_on__lte=end_date)

    manager_approval_counts = (
        queryset.values(
            "reviewed_by__id", "reviewed_by__username", "reviewed_by__email"
        )
        .annotate(approved_count=Count("id"))
        .order_by("-approved_count")[:limit]
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

    return response_data
