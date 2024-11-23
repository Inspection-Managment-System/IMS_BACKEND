from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from inspection_management.models import Evince
from users.models import User, UserProfile


def get_manager_stats(manager_id):

    try:
        manager = User.objects.get(id=manager_id)
        data_groups = manager.userprofile.data_groups.all()

        if not data_groups.exists():
            return {"error": "Manager has no associated data groups.", "status": 404}

        data_group_ids = data_groups.values_list("id", flat=True)
        evinces = Evince.objects.filter(business_unit__group_id__in=data_group_ids)

        total_evinces = evinces.filter(reviewed_by_id=manager_id).count()

        last_7_days = now() - timedelta(days=7)
        statuses = ["Approved", "Rejected", "Reassigned"]

        status_data = {}
        for status in statuses:
            overall_count = evinces.filter(
                reviewed_by_id=manager_id, status=status
            ).count()
            last_7_days_count = evinces.filter(
                reviewed_by_id=manager_id, status=status, changed_on__gte=last_7_days
            ).count()
            status_data[status.lower()] = {
                "count": overall_count,
                "last_7_days": last_7_days_count,
            }

        response_data = {
            "total_evinces": total_evinces,
            "approved_evinces": status_data["approved"],
            "rejected_evinces": status_data["rejected"],
            "reassigned_evinces": status_data["reassigned"],
            "data_groups": [
                {"id": group.id, "name": group.name} for group in data_groups
            ],
        }
        return {"data": response_data, "status": 200}

    except User.DoesNotExist:
        return {"error": "Manager not found.", "status": 404}
    except Exception as e:
        return {"error": str(e), "status": 500}
