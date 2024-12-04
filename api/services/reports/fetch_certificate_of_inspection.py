from datetime import datetime

from django.utils.timezone import make_aware

from inspection_management.models import (Evince, InspectionResult,
                                          InspectionTest)


def fetch_certificate_of_inspection(evince_id, start_date=None, end_date=None):

    evince = (
        Evince.objects.select_related(
            "business_unit", "inspection_point", "changed_by", "assigned_to"
        )
        .prefetch_related(
            "inspection_analyses",
            "inspection_analyses__inspectiontest_set",
            "inspection_analyses__analysis_type",
            "inspection_analyses__location",
            "inspection_analyses__equipment",
            "inspection_analyses__parameter_set",
        )
        .get(id=evince_id)
    )

    start_date = (
        make_aware(datetime.strptime(start_date, "%Y-%m-%d")) if start_date else None
    )
    end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d")) if end_date else None

    evince_details = {
        "id": evince.id,
        "name": evince.name,
        "description": evince.description,
        "status": evince.status,
        "changed_on": evince.changed_on,
        "logged_by": evince.changed_by.username,
        "business_unit": evince.business_unit.name,
        "inspection_point": evince.inspection_point.name,
        "start_date_time": evince.start_date_time,
        "end_date_time": evince.end_date_time,
        "assigned_to": evince.assigned_to.username if evince.assigned_to else None,
    }

    inspection_tests = [
        {
            "id": test.id,
            "inspection_analysis": test.inspection_analysis.name,
            "added_on": test.changed_on,
            "added_by": test.changed_by.username,
        }
        for analysis in evince.inspection_analyses.all()
        for test in analysis.inspectiontest_set.all()
    ]

    inspection_results = [
        {
            "id": result.id,
            "inspection_analysis": result.inspection_test.inspection_analysis.name,
            "status": result.status,
            "value": result.entered_value,
            "previous_value": result.previous_value,
            "comments": result.comments or "No Comments Added",
            "min_value": parameter.min_value,
            "max_value": parameter.max_value,
            "avg_value": parameter.avg_value,
        }
        for analysis in evince.inspection_analyses.all()
        for parameter in analysis.parameter_set.all()
        for test in analysis.inspectiontest_set.all()
        for result in InspectionResult.objects.filter(
            inspection_test=test,
            changed_on__gte=start_date if start_date else datetime.min,
            changed_on__lte=end_date if end_date else datetime.max,
        )
    ]

    return {
        "evince_details": evince_details,
        "inspection_tests": inspection_tests,
        "inspection_results": inspection_results,
    }
