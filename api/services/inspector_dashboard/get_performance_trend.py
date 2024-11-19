# services/inspector_dashboard/get_performance_trend.py
from django.db.models import Count, Q
from django.db.models.functions import TruncWeek
from django.utils import timezone
from datetime import datetime

from inspection_management.models import Evince


def get_performance_trend(inspector, start_date=None, end_date=None):
    # Base filter for evinces assigned to the inspector
    performance_filter = Q(assigned_to=inspector)

    # Parse start_date and end_date and add to filter
    if start_date:
        start_date = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        performance_filter &= Q(start_date_time__gte=start_date)

    if end_date:
        end_date = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
        performance_filter &= Q(end_date_time__lte=end_date)

    # Aggregate data weekly using TruncWeek
    trend = (
        Evince.objects.filter(performance_filter)
        .annotate(week=TruncWeek("start_date_time"))
        .values("week")
        .annotate(count=Count("id"))
        .order_by("week")
    )

    return [
        {"week": item["week"], "count": item["count"]}
        for item in trend
    ]