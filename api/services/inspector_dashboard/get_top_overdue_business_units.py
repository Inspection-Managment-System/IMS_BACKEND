from datetime import datetime

from django.db.models import Count, Max, Min, Q
from django.utils.timezone import make_aware, now

from inspection_management.models import Evince


def get_top_overdue_business_units(user, start_date=None, end_date=None, limit=5):
    """
    Get the top overdue business units based on evince count, with customizable date range and limit.

    Parameters:
        user (User): The user for which to fetch overdue evinces.
        start_date (str): The start date in "YYYY-MM-DD" format (optional).
        end_date (str): The end date in "YYYY-MM-DD" format (optional).
        limit (int): The maximum number of business units to fetch (default is 5).

    Returns:
        list: A list of dictionaries with business unit details and evince statistics.
    """
    current_time = now()

    overdue_filter = Q(
        assigned_to=user,
        status__in=["Logged", "Incomplete", "Pending"],
        end_date_time__lt=current_time,
    )

    if start_date:
        start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        overdue_filter &= Q(start_date_time__gte=start_date)
    if end_date:
        end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
        overdue_filter &= Q(end_date_time__lte=end_date)

    overdue_evinces = (
        Evince.objects.filter(overdue_filter)
        .values("inspection_point__business_unit__name")
        .annotate(
            evince_count=Count("id"),
            earliest_start=Min("start_date_time"),
            latest_end=Max("end_date_time"),
        )
        .order_by("-evince_count")[:limit]
    )

    return [
        {
            "business_unit": evince["inspection_point__business_unit__name"],
            "evince_count": evince["evince_count"],
            "earliest_start": evince["earliest_start"],
            "latest_end": evince["latest_end"],
        }
        for evince in overdue_evinces
    ]
