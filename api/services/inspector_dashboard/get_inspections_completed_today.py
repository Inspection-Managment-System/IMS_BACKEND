from django.utils import timezone

from inspection_management.models import Evince


def get_inspections_completed_today(inspector):
    today = timezone.now().date()
    completed_today = Evince.objects.filter(
        assigned_to=inspector, status="Completed", end_date_time__date=today
    )
    return {
        "completed_today_evinces_count": completed_today.count(),
        "completed_today_evinces": list(
            completed_today.values(
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
        ),
    }
