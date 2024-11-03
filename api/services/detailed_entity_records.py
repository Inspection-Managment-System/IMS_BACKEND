from django.db.models import Count, Q

from inspection_management.models import (AnalysisType, BusinessUnit, Company,
                                          DataGroup, Equipment, EquipmentType,
                                          Evince, Facility, InspectionAnalysis,
                                          InspectionPoint, Location, Parameter,
                                          Site, Suite, Unit)
from users.models import User, UserProfile


def get_model_counts():
    return {
        "inspection_point_count": InspectionPoint.objects.count(),
        "inspection_analysis_count": InspectionAnalysis.objects.count(),
        "analysis_type_count": AnalysisType.objects.count(),
        "data_group_count": DataGroup.objects.count(),
        "equipment_count": Equipment.objects.count(),
        "unit_count": Unit.objects.count(),
        "parameter_count": Parameter.objects.count(),
    }


def get_entity_breakdown_counts(user):
    return {
        "companies": (
            Company.objects.filter(changed_by=user).count()
            if hasattr(Company, "changed_by")
            else Company.objects.count()
        ),
        "sites": (
            Site.objects.filter(changed_by=user).count()
            if hasattr(Site, "changed_by")
            else Site.objects.count()
        ),
        "business_units": (
            BusinessUnit.objects.filter(changed_by=user).count()
            if hasattr(BusinessUnit, "changed_by")
            else BusinessUnit.objects.count()
        ),
        "data_groups": DataGroup.objects.count(),
        "equipment_types": (
            EquipmentType.objects.filter(changed_by=user).count()
            if hasattr(EquipmentType, "changed_by")
            else EquipmentType.objects.count()
        ),
        "equipments": (
            Equipment.objects.filter(changed_by=user).count()
            if hasattr(Equipment, "changed_by")
            else Equipment.objects.count()
        ),
        "locations": (
            Location.objects.filter(changed_by=user).count()
            if hasattr(Location, "changed_by")
            else Location.objects.count()
        ),
        "suites": (
            Suite.objects.filter(changed_by=user).count()
            if hasattr(Suite, "changed_by")
            else Suite.objects.count()
        ),
        "facilities": (
            Facility.objects.filter(changed_by=user).count()
            if hasattr(Facility, "changed_by")
            else Facility.objects.count()
        ),
        "analysis_types": (
            AnalysisType.objects.filter(changed_by=user).count()
            if hasattr(AnalysisType, "changed_by")
            else AnalysisType.objects.count()
        ),
        "units": (
            Unit.objects.filter(changed_by=user).count()
            if hasattr(Unit, "changed_by")
            else Unit.objects.count()
        ),
        "inspection_points": (
            InspectionPoint.objects.filter(changed_by=user).count()
            if hasattr(InspectionPoint, "changed_by")
            else InspectionPoint.objects.count()
        ),
        "evinces": (
            Evince.objects.filter(changed_by=user).count()
            if hasattr(Evince, "changed_by")
            else Evince.objects.count()
        ),
        "inspection_analyses": (
            InspectionAnalysis.objects.filter(changed_by=user).count()
            if hasattr(InspectionAnalysis, "changed_by")
            else InspectionAnalysis.objects.count()
        ),
    }


def get_inspector_activity_metrics():
    inspectors = User.objects.filter(userprofile__role__name="Inspector")
    if not inspectors.exists():
        return []

    inspector_metrics = inspectors.annotate(
        total_assigned=Count("assigned_inspector"),
        completed=Count(
            "assigned_inspector", filter=Q(assigned_inspector__status="Completed")
        ),
        pending=Count(
            "assigned_inspector", filter=Q(assigned_inspector__status="Logged")
        ),
    ).values("id", "username", "total_assigned", "completed", "pending")

    return list(inspector_metrics)


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
