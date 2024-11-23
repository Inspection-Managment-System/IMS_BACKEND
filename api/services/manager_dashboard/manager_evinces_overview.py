from django.db.models import Count

from inspection_management.models import Evince


def get_evince_status_overview_for_manager(user_id, data_group_ids):
    try:
        evinces = Evince.objects.filter(
            reviewed_by_id=user_id, business_unit__group_id__in=data_group_ids
        )

        status_counts = (
            evinces.values("status").annotate(count=Count("id")).order_by("status")
        )

        response_data = {entry["status"]: entry["count"] for entry in status_counts}

        all_statuses = [
            "Logged",
            "Reassigned",
            "Approved",
            "Rejected",
            "ResultsEntered",
        ]
        for status in all_statuses:
            response_data.setdefault(status, 0)

        response_data["total_evinces"] = evinces.count()

        return response_data
    except Exception as e:
        raise ValueError(f"Error fetching evince status overview: {e}")
