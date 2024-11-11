from django.db.models import Count

from inspection_management.models import Evince


def get_risk_levels(inspector):
    flammability_dist = (
        Evince.objects.filter(assigned_to=inspector)
        .values("inspection_point__flammability")
        .annotate(count=Count("id"))
        .values("inspection_point__flammability", "count")
    )

    health_risk_dist = (
        Evince.objects.filter(assigned_to=inspector)
        .values("inspection_point__health_risk")
        .annotate(count=Count("id"))
        .values("inspection_point__health_risk", "count")
    )
    result = {
        "flammability_distribution": [
            {
                "risk_level": entry["inspection_point__flammability"],
                "count": entry["count"],
            }
            for entry in flammability_dist
        ],
        "health_risk_distribution": [
            {
                "risk_level": entry["inspection_point__health_risk"],
                "count": entry["count"],
            }
            for entry in health_risk_dist
        ],
    }

    return result
