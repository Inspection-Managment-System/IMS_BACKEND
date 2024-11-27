from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
from inspection_management.models import Evince, BusinessUnit


def get_business_unit_data(manager_id, business_unit_id=None):
    """
    Fetch business units for dropdown and evince status percentages for a specific business unit.
    """
    try:
        # Fetch the manager and associated data groups
        manager = User.objects.get(id=manager_id)
        data_groups = manager.userprofile.data_groups.all()

        if not data_groups.exists():
            return {"error": "Manager has no associated data groups.", "status": 404}

        # Fetch business units associated with the manager's data groups
        business_units = BusinessUnit.objects.filter(group_id__in=data_groups.values_list("id", flat=True))

        # Prepare dropdown data
        business_unit_list = [
            {"id": bu.id, "name": bu.name}
            for bu in business_units
        ]

        # If a specific business unit is selected, calculate evince status percentages
        if business_unit_id:
            evinces = Evince.objects.filter(business_unit_id=business_unit_id)

            total_count = evinces.count()
            if total_count == 0:
                evince_percentages = {status: 0 for status in Evince.get_status_labels().keys()}
            else:
                evince_percentages = {
                    status: round((evinces.filter(status=status).count() / total_count) * 100, 2)
                    for status in Evince.get_status_labels().keys()
                }

            return {
                "business_units": business_unit_list,
                "selected_business_unit": {
                    "id": business_unit_id,
                    "name": BusinessUnit.objects.get(id=business_unit_id).name,
                    "evince_percentages": evince_percentages,
                },
            }

        # Return only the dropdown list if no business unit is selected
        return {"business_units": business_unit_list}

    except User.DoesNotExist:
        return {"error": "Manager not found.", "status": 404}
    except BusinessUnit.DoesNotExist:
        return {"error": "Business Unit not found.", "status": 404}
    except Exception as e:
        return {"error": str(e), "status": 500}