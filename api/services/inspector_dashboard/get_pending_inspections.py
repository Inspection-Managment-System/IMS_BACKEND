from datetime import datetime

from django.db.models import Q
from django.utils.timezone import make_aware

from inspection_management.models import Evince


def get_pending_inspections(User, start_date=None, end_date=None):
    pending_filter = Q(assigned_to=User, status="Logged")

    if start_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
            pending_filter &= Q(start_date_time__gte=start_date)
        except ValueError:
            raise ValueError("Invalid start_date format. Expected 'YYYY-MM-DD'.")

    if end_date:
        try:
            end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
            pending_filter &= Q(end_date_time__lte=end_date)
        except ValueError:
            raise ValueError("Invalid end_date format. Expected 'YYYY-MM-DD'.")

    pending_evinces = Evince.objects.filter(pending_filter)

    business_unit_counts = {}
    earliest_due_date = None

    for evince in pending_evinces:
        business_unit = evince.inspection_point.business_unit.name
        if business_unit not in business_unit_counts:
            business_unit_counts[business_unit] = 0
        business_unit_counts[business_unit] += 1

        due_date = evince.end_date_time
        if due_date and (earliest_due_date is None or due_date < earliest_due_date):
            earliest_due_date = due_date

    return {
        "pending_evinces_count": pending_evinces.count(),
        "most_active_business_unit": max(
            business_unit_counts, key=business_unit_counts.get, default=None
        ),
        "earliest_due_date": (
            earliest_due_date.isoformat() if earliest_due_date else None
        ),
        "pending_evinces": list(
            pending_evinces.values(
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
