from inspection_management.models import Evince


def get_pending_inspections(inspector):
    pending_evinces = Evince.objects.filter(assigned_to=inspector, status="Logged")
    return {
        "pending_evinces_count": pending_evinces.count(),
        "pending_evinces": list(
            pending_evinces.values(
                "id",
                "name",
                "description",
                "status",
                "start_date_time",
                "end_date_time",
                "assigned_to__username",
                "reviewed_by__username",
                "inspection_point__name",
                "inspection_point__business_unit__name",
                "reassigned",
            )
        ),
    }
