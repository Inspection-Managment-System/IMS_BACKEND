from inspection_management.models import BusinessUnit, Evince
from users.models import User


def fetch_business_units_and_evinces(user, business_unit_id=None):

    if not user.userprofile.role.name == "Manager":
        raise ValueError("Only managers can access this resource.")

    data_groups = user.userprofile.data_groups.all()

    if not data_groups.exists():
        return {"business_units": [], "evinces": []}

    business_units = BusinessUnit.objects.filter(group__in=data_groups).select_related(
        "site", "group"
    )

    business_unit_data = [
        {
            "id": bu.id,
            "name": bu.name,
            "description": bu.description,
            "site": bu.site.name,
        }
        for bu in business_units
    ]

    evince_data = []
    if business_unit_id:
        approved_evinces = Evince.objects.filter(
            status="Approved", business_unit_id=business_unit_id
        ).select_related("business_unit")

        evince_data = [
            {
                "id": evince.id,
                "name": evince.name,
                "description": evince.description,
                "business_unit": evince.business_unit.name,
            }
            for evince in approved_evinces
        ]

    return {"evinces": evince_data}
