from django.db.models import Count, Q

from inspection_management.models import Evince
from users.models import User


def get_inspector_activity_metrics(user_id=None):
    if user_id:
        inspector = User.objects.filter(
            id=user_id, userprofile__role__name="Inspector"
        ).first()
        if not inspector:
            return {"detail": "Inspector not found"}

        metrics = {
            "id": inspector.id,
            "username": inspector.username,
            "total_assigned": Evince.objects.filter(assigned_to=inspector).count(),
            "completed": Evince.objects.filter(
                assigned_to=inspector, status="Completed"
            ).count(),
            "pending": Evince.objects.filter(
                assigned_to=inspector, status="Logged"
            ).count(),
        }
        return metrics

    inspectors = (
        User.objects.filter(userprofile__role__name="Inspector")
        .annotate(
            total_assigned=Count("evince"),
            completed=Count("evince", filter=Q(evince__status="Completed")),
            pending=Count("evince", filter=Q(evince__status="Logged")),
        )
        .values("id", "username", "total_assigned", "completed", "pending")
    )

    return list(inspectors)
