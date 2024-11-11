# services/inspector_dashboard/get_performance_trend.py
from django.db.models import Count
from django.db.models.functions import TruncWeek

from inspection_management.models import Evince


def get_performance_trend(inspector):
    return (
        Evince.objects.filter(assigned_to=inspector, status="Approved")
        .annotate(week=TruncWeek("end_date_time"))
        .values("week")
        .annotate(count=Count("id"))
        .order_by("week")
    )
