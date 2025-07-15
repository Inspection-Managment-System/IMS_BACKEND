from django.db.models import Count

from inspection_management.models import Evince
from users.models import User


def get_top_business_units(manager_id):
    """
    Fetch the top 5 business units by evinces count within the manager's data groups.
    """
    try:
        manager = User.objects.get(id=manager_id)
        data_groups = manager.userprofile.data_groups.all()

        if not data_groups.exists():
            return {"error": "Manager has no associated data groups.", "status": 404}

        data_group_ids = data_groups.values_list("id", flat=True)

        evinces = Evince.objects.filter(business_unit__group_id__in=data_group_ids)

        top_business_units = (
            evinces.values("business_unit__id", "business_unit__name")
            .annotate(evinces_count=Count("id"))
            .order_by("-evinces_count")[:5]
        )

        data = [
            {
                "id": unit["business_unit__id"],
                "name": unit["business_unit__name"],
                "evinces_count": unit["evinces_count"],
            }
            for unit in top_business_units
        ]

        return {"data": data, "status": 200}

    except User.DoesNotExist:
        return {"error": "Manager not found.", "status": 404}
    except Exception as e:
        return {"error": str(e), "status": 500}
