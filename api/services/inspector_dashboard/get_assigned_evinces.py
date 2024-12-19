from django.db.models import Q

from inspection_management.models import Evince


def get_assigned_evinces(user):
    return Evince.objects.filter(assigned_to=user).values(
        "name", "status", "start_date_time", "end_date_time"
    )
