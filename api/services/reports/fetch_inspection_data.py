from datetime import datetime

from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F

from inspection_management.models import BusinessUnit, Evince


def fetch_inspection_data(start_date=None, end_date=None, business_unit_id=None):

    filters = {}
    if start_date:
        filters["start_date_time__gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        filters["end_date_time__lte"] = datetime.strptime(end_date, "%Y-%m-%d")
    if business_unit_id:
        filters["business_unit_id"] = business_unit_id

    evinces = Evince.objects.filter(**filters)

    business_unit_data = []
    business_units = BusinessUnit.objects.filter(
        id__in=evinces.values_list("business_unit_id", flat=True)
    ).distinct()

    for business_unit in business_units:
        unit_evinces = evinces.filter(business_unit=business_unit)

        status_counts = unit_evinces.values("status").annotate(count=Count("status"))
        total_inspections = unit_evinces.count()
        statuses = {
            status["status"]: {
                "count": status["count"],
                "percentage": round((status["count"] / total_inspections) * 100, 2),
            }
            for status in status_counts
        }

        duration_field = ExpressionWrapper(
            F("end_date_time") - F("start_date_time"), output_field=DurationField()
        )
        average_completion_time = unit_evinces.annotate(
            duration=duration_field
        ).aggregate(avg_duration=Avg("duration"))["avg_duration"]

        business_unit_data.append(
            {
                "name": business_unit.name,
                "total_inspections": total_inspections,
                "statuses": statuses,
                "average_completion_time": (
                    str(average_completion_time) if average_completion_time else "N/A"
                ),
            }
        )

    return business_unit_data
