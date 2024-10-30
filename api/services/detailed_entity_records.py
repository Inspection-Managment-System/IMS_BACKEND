from inspection_management.models import (AnalysisType, DataGroup, Equipment,
                                          InspectionAnalysis, InspectionPoint,
                                          Parameter, Unit)


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
