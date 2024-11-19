from django.utils import timezone

from inspection_management.models import Evince
from datetime import datetime
from django.db.models import Q

def get_overdue_inspections(user, start_date=None, end_date=None):
    current_time = timezone.now()

    # Base filter for overdue inspections
    overdue_filter = Q(status__in=["Logged", "Incomplete", "Pending"], end_date_time__lt=current_time)

    # Parse the date parameters to handle date-only input
    if start_date:
        start_date = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        end_date = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    # Apply range filtering
    if start_date and end_date:
        overdue_filter &= (
            Q(start_date_time__gte=start_date, start_date_time__lte=end_date) |  # Starts within range
            Q(end_date_time__gte=start_date, end_date_time__lte=end_date) |      # Ends within range
            Q(start_date_time__lte=start_date, end_date_time__gte=end_date)     # Spans across range
        )
    elif start_date:
        overdue_filter &= Q(end_date_time__gte=start_date)  # Ends after or on start_date
    elif end_date:
        overdue_filter &= Q(start_date_time__lte=end_date)  # Starts before or on end_date

    # Retrieve overdue evinces based on the updated filter
    overdue_evinces = Evince.objects.filter(overdue_filter)

    return {
        "over_due_evinces_count": overdue_evinces.count(),
        "over_due_evinces": list(
            overdue_evinces.values(
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
                "reassigned",
            )
        ),
    }