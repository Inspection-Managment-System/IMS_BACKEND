from django.db.models import Count, Q
from django.utils.timezone import now
from datetime import datetime, timedelta
from rest_framework.decorators import action
from rest_framework.response import Response

from inspection_management.models import Evince


def get_evinces_summary_with_details(user):
    today = now().date()
    start_of_month = today.replace(day=1)
    previous_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    previous_month_end = start_of_month - timedelta(days=1)

    evinces = Evince.objects.filter(assigned_to=user)

    current_month_approved = evinces.filter(
        status="Approved", start_date_time__gte=start_of_month
    )
    current_month_today = evinces.filter(start_date_time__date=today)
    current_month_upcoming = evinces.filter(start_date_time__gt=today)
    current_month_overdue = evinces.filter(
        end_date_time__lt=now(), status="Logged"
    )

    previous_month_approved = evinces.filter(
        status="Approved",
        start_date_time__gte=previous_month_start,
        start_date_time__lt=start_of_month,
    ).count()

    return {
        "assigned_approved_details": {
            "total": current_month_approved.count(),
            "growth": current_month_approved.count() - previous_month_approved,
            "details": list(
                current_month_approved.values(
                    "id",
                    "name",
                    "description",
                    "status",
                    "start_date_time",
                    "end_date_time",
                    "inspection_point__name",
                    "inspection_point__business_unit__name",
                    "assigned_to__username",
                    "reviewed_by__username",
                    "reassigned",
                )
            ),
        },
        "assigned_today_evinces_details": {
            "total": current_month_today.count(),
            "growth": current_month_today.count(),
            "details": list(
                current_month_today.values(
                    "id",
                    "name",
                    "description",
                    "status",
                    "start_date_time",
                    "end_date_time",
                    "inspection_point__name",
                    "inspection_point__business_unit__name",
                    "assigned_to__username",
                    "reviewed_by__username",
                    "reassigned",
                )
            ),
        },
        "assigned_upcoming_evinces_details": {
            "total": current_month_upcoming.count(),
            "growth": current_month_upcoming.count(),
            "details": list(
                current_month_upcoming.values(
                    "id",
                    "name",
                    "description",
                    "status",
                    "start_date_time",
                    "end_date_time",
                    "inspection_point__name",
                    "inspection_point__business_unit__name",
                    "assigned_to__username",
                    "reviewed_by__username",
                    "reassigned",
                )
            ),
        },
        "assigned_overdue_evinces_details": {
            "total": current_month_overdue.count(),
            "growth": current_month_overdue.count(),
            "details": list(
                current_month_overdue.values(
                    "id",
                    "name",
                    "description",
                    "status",
                    "start_date_time",
                    "end_date_time",
                    "inspection_point__name",
                    "inspection_point__business_unit__name",
                    "assigned_to__username",
                    "reviewed_by__username",
                    "reassigned",
                )
            ),
        },
    }





