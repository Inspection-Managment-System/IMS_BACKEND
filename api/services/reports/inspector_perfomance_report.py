from datetime import datetime

from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q

from inspection_management.models import Evince, InspectionResult, Parameter


def single_inspector_performance(user, start_date=None, end_date=None):

    filters = {"assigned_to": user}
    if start_date:
        filters["start_date_time__gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        filters["end_date_time__lte"] = datetime.strptime(end_date, "%Y-%m-%d")

    evinces = Evince.objects.filter(**filters)

    if not evinces.exists():
        return {
            "summary": {
                "inspector_name": None,
                "total_inspections": 0,
                "completed_inspections": 0,
                "pending_inspections": 0,
                "result_entered": 0,
                "reassigned": 0,
                "average_completion_time": "N/A",
            },
            "details": [],
            "message": "No records found for the selected inspector and date range.",
        }

    inspector_name = evinces.first().assigned_to.username

    total_inspections = evinces.count()
    completed_inspections = evinces.filter(status="Approved").count()
    pending_inspections = evinces.filter(status="Logged").count()
    result_entered = evinces.filter(status="ResultsEntered").count()
    reassigned = evinces.filter(status="Reassigned").count()

    approved_evinces = evinces.filter(status="Approved")
    avg_time = approved_evinces.annotate(
        duration=ExpressionWrapper(
            F("end_date_time") - F("start_date_time"), output_field=DurationField()
        )
    ).aggregate(Avg("duration"))["duration__avg"]

    risk_summary = {
        "high_flammability_count": evinces.filter(
            inspection_point__flammability="High"
        ).count(),
        "medium_health_risk_count": evinces.filter(
            inspection_point__health_risk="Medium"
        ).count(),
        "low_risk_count": evinces.filter(
            Q(inspection_point__flammability="Low")
            & Q(inspection_point__health_risk="Low")
        ).count(),
    }

    parameter_violations = []
    for parameter in Parameter.objects.all():
        violations = InspectionResult.objects.filter(
            inspection_test__evince__in=evinces,
            inspection_test__inspection_analysis__parameter=parameter,
        ).filter(
            Q(entered_value__lt=parameter.min_value)
            | Q(entered_value__gt=parameter.max_value)
        )
        parameter_violations.append(
            {
                "parameter_name": parameter.name,
                "violations_count": violations.count(),
                "violated_inspections": list(
                    violations.values("inspection_test__evince__id", "entered_value")
                ),
                "min_value": parameter.min_value,
                "max_value": parameter.max_value,
            }
        )

    details = [
        {
            "id": evince.id,
            "name": evince.name,
            "status": evince.status,
            "start_date_time": evince.start_date_time,
            "end_date_time": evince.end_date_time,
            "inspection_point": {
                "name": evince.inspection_point.name,
                "description": evince.inspection_point.description,
                "flammability": evince.inspection_point.flammability,
                "health_risk": evince.inspection_point.health_risk,
            },
            "business_unit": {
                "name": evince.business_unit.name,
                "site": evince.business_unit.site.name,
                "company": evince.business_unit.site.company.name,
            },
            "analysis_details": list(
                evince.inspection_analyses.values(
                    "name",
                    "description",
                    "equipment__name",
                    "location__address",
                    "analysis_type__name",
                )
            ),
        }
        for evince in evinces
    ]

    return {
        "summary": {
            "inspector_name": inspector_name,
            "total_inspections": total_inspections,
            "completed_inspections": completed_inspections,
            "pending_inspections": pending_inspections,
            "result_entered": result_entered,
            "reassigned": reassigned,
            "average_completion_time": str(avg_time) if avg_time else "N/A",
        },
        "risk_summary": risk_summary,
        "parameter_violations": parameter_violations,
        "details": details,
    }
