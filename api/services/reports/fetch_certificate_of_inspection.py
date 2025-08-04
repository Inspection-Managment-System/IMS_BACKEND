from datetime import datetime

from django.utils.timezone import make_aware

from inspection_management.models import (Evince, InspectionResult,
                                          InspectionTest, Parameter)


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
        "inspector": evince.assigned_to.username if evince.assigned_to else "Not Assigned",
        "manager": evince.reviewed_by.username if evince.reviewed_by else "Not Assigned",
        "approved_by": evince.reviewed_by.username if evince.reviewed_by and evince.status == "Approved" else "Not Approved",
    }

    inspection_tests = [
        {
            "id": test.id,
            "inspection_analysis": test.inspection_analysis.name,
            "added_on": test.changed_on,
            "added_by": test.changed_by.username,
        }
        for test in InspectionTest.objects.filter(evince=evince)
    ]

    # Get all results for this evince using the same approach as the evince results endpoint
    inspection_results = InspectionResult.objects.filter(evince_id=evince.id).select_related(
        "inspection_test__inspection_analysis"
    )
    
    # Get all parameters for the inspection analyses in this evince
    related_parameters = Parameter.objects.filter(
        inspection_analysis__inspectiontest__evince_id=evince.id
    ).distinct()

    # Create a list of results with parameter information (same logic as evince results endpoint)
    all_results = []
    for i, result in enumerate(inspection_results):
        # Get the corresponding parameter (assuming one result per parameter)
        parameter = related_parameters[i] if i < len(related_parameters) else None
        
        if parameter:
            # Handle different parameter types for display values and expected values
            display_value = result.entered_value
            expected_value = ""
            
            if parameter.string_value == "checklist":
                # For checklist parameters
                if result.entered_value == "checked":
                    if parameter.checklist_data_type == "satisfactory_unsatisfactory":
                        display_value = "Satisfactory"
                        expected_value = "Satisfactory/Unsatisfactory"
                    elif parameter.checklist_data_type == "true_false":
                        display_value = "True"
                        expected_value = "True/False"
                    else:  # yes_no
                        display_value = "Yes"
                        expected_value = "Yes/No"
                elif result.entered_value == "unchecked":
                    if parameter.checklist_data_type == "satisfactory_unsatisfactory":
                        display_value = "Unsatisfactory"
                        expected_value = "Satisfactory/Unsatisfactory"
                    elif parameter.checklist_data_type == "true_false":
                        display_value = "False"
                        expected_value = "True/False"
                    else:  # yes_no
                        display_value = "No"
                        expected_value = "Yes/No"
                else:
                    # Handle cases where the value might be the actual option text
                    expected_value = "Satisfactory/Unsatisfactory" if parameter.checklist_data_type == "satisfactory_unsatisfactory" else \
                                  "True/False" if parameter.checklist_data_type == "true_false" else "Yes/No"
            elif parameter.string_value:
                # For string parameters
                expected_value = parameter.string_value
            else:
                # For numeric parameters - show descriptive expected value with labels
                min_val = parameter.min_value or 0
                avg_val = parameter.avg_value or 0
                max_val = parameter.max_value or 0
                expected_value = f"Min: {min_val}, Avg: {avg_val}, Max: {max_val}"
                # Don't modify display_value for numeric parameters - keep the actual entered value
            
            result_data = {
                "id": result.id,
                "inspection_analysis": parameter.name,
                "status": result.status,
                "value": display_value,
                "previous_value": result.previous_value,
                "comments": result.comments or "No Comments Added",
                "min_value": parameter.min_value,
                "max_value": parameter.max_value,
                "avg_value": parameter.avg_value,
                "expected_value": expected_value,
            }
            
            all_results.append(result_data)

    return {
        "evince_details": evince_details,
        "inspection_tests": inspection_tests,
        "inspection_results": all_results,
    }
