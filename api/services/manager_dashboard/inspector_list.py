from django.db.models import Count

from inspection_management.models import DataGroup, Evince
from users.models import User


def get_inspectors_list(manager_id):
    try:
        user = User.objects.get(id=manager_id)
        data_groups = user.userprofile.data_groups.all()

        if not data_groups.exists():
            raise ValueError("Manager has no associated data groups.")

        inspectors = User.objects.filter(
            userprofile__role__name="Inspector",
            userprofile__data_groups__in=data_groups,
        ).distinct()

        return [
            {"id": inspector.id, "name": inspector.username} for inspector in inspectors
        ]

    except User.DoesNotExist:
        raise ValueError("Manager not found.")
    except Exception as e:
        raise ValueError(f"Error fetching inspectors: {e}")
