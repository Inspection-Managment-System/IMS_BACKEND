from django.db.models import Q

from inspection_management.models import InspectionResult, Parameter


def fetch_generic_facility_functionality_report(start_date=None, end_date=None):

    filters = {}
    if start_date:
        filters["inspection_test__evince__start_date_time__gte"] = start_date
    if end_date:
        filters["inspection_test__evince__end_date_time__lte"] = end_date

    yes_no_parameters = Parameter.objects.filter(
        Q(string_value__icontains="Yes") | Q(string_value__icontains="No")
    )

    report_data = []

    for parameter in yes_no_parameters:
        results = InspectionResult.objects.filter(
            inspection_test__inspection_analysis__parameter=parameter, **filters
        )

        total_count = results.count()
        functional_count = results.filter(entered_value__iexact="Yes").count()
        not_functional_count = results.filter(entered_value__iexact="No").count()
        not_entered_count = results.filter(entered_value__isnull=True).count()

        working_percentage = (
            (functional_count / total_count * 100) if total_count else 0
        )
        not_working_percentage = (
            (not_functional_count / total_count * 100) if total_count else 0
        )

        if working_percentage >= 85:
            condition_message = "The condition of the facility is good."
        else:
            condition_message = "There are areas that need improvement."

        report_data.append(
            {
                "parameter": parameter.name,
                "total_count": total_count,
                "functional_count": functional_count,
                "not_functional_count": not_functional_count,
                "not_entered_count": not_entered_count,
                "working_percentage": round(working_percentage, 2),
                "not_working_percentage": round(not_working_percentage, 2),
                "condition": condition_message,
            }
        )

    return report_data
