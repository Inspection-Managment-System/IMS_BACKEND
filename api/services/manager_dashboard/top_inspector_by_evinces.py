from django.db.models import Count

from inspection_management.models import DataGroup, Evince


def get_top_inspectors_by_evinces(manager_id, data_group_ids, inspector_id=None):
    try:
        evinces = Evince.objects.filter(
            business_unit__group_id__in=data_group_ids,
            reviewed_by_id=manager_id,
        )

        if inspector_id:
            evinces = evinces.filter(assigned_to_id=inspector_id)

        inspector_counts = (
            evinces.values("assigned_to_id", "assigned_to__username")
            .annotate(evince_count=Count("id"))
            .order_by("-evince_count")
        )

        response_data = []
        for entry in inspector_counts:
            status_counts = (
                evinces.filter(assigned_to_id=entry["assigned_to_id"])
                .values("status")
                .annotate(count=Count("id"))
            )
            status_counts_dict = {
                item["status"]: item["count"] for item in status_counts
            }

            all_statuses = [
                "Logged",
                "ResultsEntered",
                "Approved",
                "Reassigned",
                "Rejected",
            ]
            for status in all_statuses:
                status_counts_dict.setdefault(status, 0)

            response_data.append(
                {
                    "inspector_id": entry["assigned_to_id"],
                    "inspector_name": entry["assigned_to__username"],
                    "total_evinces": entry["evince_count"],
                    "status_counts": status_counts_dict,
                    "data_groups": [
                        {"id": dg.id, "name": dg.name}
                        for dg in DataGroup.objects.filter(
                            user_profiles__user_id=entry["assigned_to_id"]
                        )
                    ],
                }
            )

        return response_data

    except Exception as e:
        raise ValueError(f"Error fetching top inspectors by evinces: {e}")
