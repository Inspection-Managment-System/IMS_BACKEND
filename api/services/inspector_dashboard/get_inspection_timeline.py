from django.db.models import BooleanField, Case, ExpressionWrapper, F, Value, When
from django.utils import timezone

from inspection_management.models import Evince


def get_inspection_timeline(user):
    current_time = timezone.now()
    return (
        Evince.objects.filter(assigned_to=user)
        .values("id", "name", "start_date_time", "end_date_time", "status")
        .annotate(
            is_overdue=Case(
                When(end_date_time__lt=current_time, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
    )
