from datetime import timedelta

from django.db.models import Count
from django.utils.timezone import now

from inspection_management.models import Evince
from users.models import User


def get_manager_stats(manager_id):
    try:
        manager = User.objects.get(id=manager_id)
        data_groups = manager.userprofile.data_groups.all()

        if not data_groups.exists():
            return {"error": "Manager has no associated data groups.", "status": 404}

        data_group_ids = data_groups.values_list("id", flat=True)
        evinces = Evince.objects.filter(business_unit__group_id__in=data_group_ids)

        # Timeframe calculations
        last_7_days = now() - timedelta(days=7)
        last_30_days = now() - timedelta(days=30)

        # Calculate total evinces
        total_evinces = evinces.filter(reviewed_by_id=manager_id).count()
        total_evinces_last_7_days = evinces.filter(
            reviewed_by_id=manager_id, changed_on__gte=last_7_days
        ).count()
        total_evinces_last_30_days = evinces.filter(
            reviewed_by_id=manager_id, changed_on__gte=last_30_days
        ).count()

        statuses = ["Approved", "Rejected", "Reassigned"]
        status_data = {}

        # Calculate overall count, last 7 days count, and last month count for each status
        for status in statuses:
            overall_count = evinces.filter(
                reviewed_by_id=manager_id, status=status
            ).count()
            last_7_days_count = evinces.filter(
                reviewed_by_id=manager_id, status=status, changed_on__gte=last_7_days
            ).count()
            last_month_count = evinces.filter(
                reviewed_by_id=manager_id, status=status, changed_on__gte=last_30_days
            ).count()
            status_data[status.lower()] = {
                "count": overall_count,
                "last_7_days": last_7_days_count,
                "this_month": last_month_count,
            }

        response_data = {
            "total_evinces": {
                "count": total_evinces,
                "last_7_days": total_evinces_last_7_days,
                "this_month": total_evinces_last_30_days,
            },
            "approved_evinces": status_data["approved"],
            "rejected_evinces": status_data["rejected"],
            "reassigned_evinces": status_data["reassigned"],
        }
        return {"data": response_data, "status": 200}

    except User.DoesNotExist:
        return {"error": "Manager not found.", "status": 404}
    except Exception as e:
        return {"error": str(e), "status": 500}
