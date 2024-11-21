from django.db.models import Count

from inspection_management.models import DataGroup, Evince


def get_top_business_units_by_evince_count(user_id, limit=5):

    data_groups = DataGroup.objects.filter(user_profiles__user_id=user_id)

    if not data_groups.exists():
        return []

    queryset = Evince.objects.filter(business_unit__group__in=data_groups)

    evince_counts = (
        queryset.values("business_unit__name")
        .annotate(evince_count=Count("id"))
        .order_by("-evince_count")[:limit]
    )

    response_data = [
        {
            "business_unit_name": item["business_unit__name"],
            "evince_count": item["evince_count"],
        }
        for item in evince_counts
    ]

    return response_data
