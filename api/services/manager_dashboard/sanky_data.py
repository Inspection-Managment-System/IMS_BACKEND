from inspection_management.models import Evince
from users.models import User


def get_manager_sunburst_data(manager_id):
    """
    Fetch data for the Sunburst chart showing evinces grouped by data groups and statuses
    specifically for the manager's assigned data groups.
    """
    try:
        manager = User.objects.get(id=manager_id)
        data_groups = manager.userprofile.data_groups.all()

        if not data_groups.exists():
            return {"error": "Manager has no associated data groups.", "status": 404}

        data_group_ids = data_groups.values_list("id", flat=True)

        evinces = Evince.objects.filter(business_unit__group_id__in=data_group_ids)

        data = []
        for group in data_groups:
            group_data = {"name": group.name, "children": []}

            statuses = [
                "Approved",
                "Logged",
                "Rejected",
                "ResultsEntered",
                "Reassigned",
            ]
            for status in statuses:
                count = evinces.filter(
                    business_unit__group_id=group.id, status=status
                ).count()

                if count > 0:
                    group_data["children"].append({"name": status, "value": count})

            if group_data["children"]:
                data.append(group_data)

        return {"data": data}

    except User.DoesNotExist:
        return {"error": "Manager not found.", "status": 404}
    except Exception as e:
        return {"error": str(e), "status": 500}
