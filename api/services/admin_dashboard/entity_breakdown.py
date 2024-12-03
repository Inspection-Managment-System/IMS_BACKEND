from inspection_management.models import (
    AnalysisType,
    BusinessUnit,
    Company,
    DataGroup,
    Equipment,
    EquipmentType,
    Evince,
    Facility,
    InspectionAnalysis,
    InspectionPoint,
    Location,
    Site,
    Suite,
    Unit,
)


def get_entity_breakdown_counts(user):
    try:
        user_data_groups = user.userprofile.data_groups.all()
    except AttributeError:
        return {"error": "User does not have assigned data groups."}

    if not user_data_groups.exists():
        return {"error": "No data groups assigned to the user."}

    data_group_ids = user_data_groups.values_list("id", flat=True)

    return {
        "companies": Company.objects.filter(group__id__in=data_group_ids).count(),
        "sites": Site.objects.filter(group__id__in=data_group_ids).count(),
        "business_units": BusinessUnit.objects.filter(
            group__id__in=data_group_ids
        ).count(),
        "data_groups": DataGroup.objects.filter(id__in=data_group_ids).count(),
        "equipment_types": EquipmentType.objects.filter(
            group__id__in=data_group_ids
        ).count(),
        "equipments": Equipment.objects.filter(group__id__in=data_group_ids).count(),
        "locations": Location.objects.filter(group__id__in=data_group_ids).count(),
        "suites": Suite.objects.filter(group__id__in=data_group_ids).count(),
        "facilities": Facility.objects.filter(group__id__in=data_group_ids).count(),
        "analysis_types": AnalysisType.objects.filter(
            group__id__in=data_group_ids
        ).count(),
        "units": Unit.objects.filter(group__id__in=data_group_ids).count(),
        "inspection_points": InspectionPoint.objects.filter(
            group__id__in=data_group_ids
        ).count(),
        "evinces": Evince.objects.filter(
            business_unit__group__id__in=data_group_ids
        ).count(),
        "inspection_analyses": InspectionAnalysis.objects.filter(
            group__id__in=data_group_ids
        ).count(),
    }
