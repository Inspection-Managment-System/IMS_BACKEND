from django.db.models import Count

from inspection_management.models import Evince


def get_inspection_status_breakdown(user):
    all_statuses = ["Approved", "Rejected", "Logged", "Result Entered"]
    status_counts = (
        Evince.objects.filter(assigned_to=user)
        .values("status")
        .annotate(count=Count("status"))
    )

    evinces_by_status = Evince.objects.filter(assigned_to=user).values(
        "id",
        "name",
        "description",
        "status",
        "start_date_time",
        "end_date_time",
        "assigned_to__username",
        "reviewed_by__username",
        "inspection_point__name",
        "inspection_point__business_unit__name",
    )
    breakdown = {status: {"count": 0, "Evinces": []} for status in all_statuses}
    for item in status_counts:
        status = item["status"]
        breakdown[status]["count"] = item["count"]
        breakdown[status]["Evinces"] = [
            evince for evince in evinces_by_status if evince["status"] == status
        ]

    return breakdown
