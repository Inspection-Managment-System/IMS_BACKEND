from django.utils import timezone

from inspection_management.models import Evince


def get_overdue_inspections(inspector):
    current_time = timezone.now()
    overdue_evinces = Evince.objects.filter(
        status__in=["Logged", "Incomplete", "Pending"], end_date_time__lt=current_time
    )
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
