from django.db.models import Avg, F

from inspection_management.models import Evince
from users.models import User


def get_average_processing_time(manager_id):

    try:
        manager = User.objects.get(id=manager_id)
        data_groups = manager.userprofile.data_groups.all()

        if not data_groups.exists():
            return {"error": "Manager has no associated data groups.", "status": 404}

        data_group_ids = data_groups.values_list("id", flat=True)

        evinces = Evince.objects.filter(business_unit__group_id__in=data_group_ids)

        avg_time = (
            evinces.annotate(processing_time=F("changed_on") - F("start_date_time"))
            .values("status")
            .annotate(average_time=Avg("processing_time"))
        )

        result = {
            entry["status"]: entry["average_time"].total_seconds() / 3600
            for entry in avg_time
        }
        return {"average_time": result, "status": 200}

    except User.DoesNotExist:
        return {"error": "Manager not found.", "status": 404}
    except Exception as e:
        return {"error": str(e), "status": 500}
