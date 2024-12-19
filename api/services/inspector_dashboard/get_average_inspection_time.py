from django.db.models import Avg, DurationField, ExpressionWrapper, F

from inspection_management.models import Evince


def get_average_inspection_time(user):
    approved_evinces = (
        Evince.objects.filter(assigned_to=user, status="Approved")
        .annotate(
            duration=ExpressionWrapper(
                F("end_date_time") - F("start_date_time"), output_field=DurationField()
            )
        )
        .values("id", "name", "duration")
    )

    result = []
    for entry in approved_evinces:
        duration_seconds = entry["duration"].total_seconds() if entry["duration"] else 0
        duration_hours = round(duration_seconds / 3600, 2)
        duration_days = int(duration_seconds // (3600 * 24))
        duration_weeks = int(duration_seconds // (3600 * 24 * 7))

        result.append(
            {
                "evince_id": entry["id"],
                "evince_name": entry["name"],
                "duration_hours": duration_hours,
                "duration_days": duration_days,
                "duration_weeks": duration_weeks,
            }
        )

    return result
