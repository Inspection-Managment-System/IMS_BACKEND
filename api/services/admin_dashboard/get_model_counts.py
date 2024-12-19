from django.core.exceptions import ObjectDoesNotExist

from inspection_management.models import (AnalysisType, DataGroup, Equipment,
                                          Evince, InspectionAnalysis,
                                          InspectionPoint, Parameter, Unit)
from users.models import User


def get_model_counts(user_id):
    try:
        user = User.objects.get(id=int(user_id))
        user_profile = user.userprofile
        data_groups = user_profile.data_groups.all()
        data_group_filters = [{"id": dg.id, "name": dg.name} for dg in data_groups]
    except (ObjectDoesNotExist, ValueError, AttributeError):

        return {
            "inspection_point_count": 0,
            "inspection_analysis_count": 0,
            "analysis_type_count": 0,
            "evinces_count": 0,
            "data_group_count": 0,
            "equipment_count": 0,
            "unit_count": 0,
            "parameter_count": 0,
        }

    if not data_group_filters:
        return {
            "inspection_point_count": 0,
            "inspection_analysis_count": 0,
            "analysis_type_count": 0,
            "evinces_count": 0,
            "data_group_count": 0,
            "equipment_count": 0,
            "unit_count": 0,
            "parameter_count": 0,
        }

    inspection_point_count = InspectionPoint.objects.filter(
        group__id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    inspection_analysis_count = InspectionAnalysis.objects.filter(
        group__id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    analysis_type_count = AnalysisType.objects.filter(
        group__id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    evinces_count = Evince.objects.filter(
        business_unit__group__id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    data_group_count = DataGroup.objects.filter(
        id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    equipment_count = Equipment.objects.filter(
        group__id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    unit_count = Unit.objects.filter(
        group__id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    parameter_count = Parameter.objects.filter(
        group__id__in=[dg["id"] for dg in data_group_filters]
    ).count()

    return {
        "inspection_point_count": inspection_point_count,
        "inspection_analysis_count": inspection_analysis_count,
        "analysis_type_count": analysis_type_count,
        "evinces_count": evinces_count,
        "data_group_count": data_group_count,
        "equipment_count": equipment_count,
        "unit_count": unit_count,
        "parameter_count": parameter_count,
    }
