from django.db.models import Count, Q
from django.utils import timezone

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
        "evinces_count": Evince.objects.count(),
        "data_group_count": DataGroup.objects.count(),
        "equipment_count": Equipment.objects.count(),
        "unit_count": Unit.objects.count(),
        "parameter_count": Parameter.objects.count(),
    }


def statistic_cards_data():
    current_date = timezone.now()
    current_month_start = current_date.replace(day=1)  # Start of the current month

    # Count total and current month additions for each model
    total_users = User.objects.count()
    users_this_month = User.objects.filter(date_joined__gte=current_month_start).count()
    
    total_companies = Company.objects.count()
    companies_this_month = Company.objects.filter(changed_on__gte=current_month_start).count()
    
    total_business_units = BusinessUnit.objects.count()
    business_units_this_month = BusinessUnit.objects.filter(changed_on__gte=current_month_start).count()
    
    total_sites = Site.objects.count()
    sites_this_month = Site.objects.filter(changed_on__gte=current_month_start).count()

    return {
        "total_users": {"count": total_users, "this_month": users_this_month},
        "total_companies": {"count": total_companies, "this_month": companies_this_month},
        "total_business_unit": {"count": total_business_units, "this_month": business_units_this_month},
        "totalsites": {"count": total_sites, "this_month": sites_this_month},
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


def get_evince_status_counts():
    evince_status_counts = Evince.objects.values("status").annotate(count=Count("id"))
    status_counts = {entry["status"]: entry["count"] for entry in evince_status_counts}
    all_statuses = ["Approved", "Rejected", "ResultsEntered", "Logged"]
    for status in all_statuses:
        if status not in status_counts:
            status_counts[status] = 0
    total_evinces = sum(status_counts.values())
    status_counts["total_evinces"] = total_evinces
    return status_counts
