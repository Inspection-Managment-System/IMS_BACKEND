from django.db.models import Count

from inspection_management.models import Evince


def get_inspection_status_breakdown(inspector):
    status_counts = (
        Evince.objects.filter(assigned_to=inspector)
        .values("status")
        .annotate(count=Count("status"))
    )
    evinces_by_status = Evince.objects.filter(assigned_to=inspector).values(
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

    breakdown = {}
    for item in status_counts:
        status = item["status"]
        breakdown[status] = {
            "count": item["count"],
            "Evinces": [
                evince for evince in evinces_by_status if evince["status"] == status
            ],
        }

    return breakdown
