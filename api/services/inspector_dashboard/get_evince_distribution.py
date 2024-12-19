from django.db.models import Count

from inspection_management.models import Evince


def get_evinces_distribution(inspector):
    return (
        Evince.objects.filter(assigned_to=inspector)
        .values("status")
        .annotate(count=Count("status"))
    )
