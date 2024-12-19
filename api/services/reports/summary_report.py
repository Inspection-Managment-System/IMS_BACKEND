from django.db.models import Count

from inspection_management.models import (AnalysisType, BusinessUnit, Company,
                                          DataGroup, Equipment, Evince,
                                          Facility, InspectionAnalysis,
                                          InspectionPoint, Parameter, Site,
                                          Suite, Unit)


def fetch_summary_report():

    entity_counts = {
        "companies": Company.objects.count(),
        "sites": Site.objects.count(),
        "business_units": BusinessUnit.objects.count(),
        "inspection_points": InspectionPoint.objects.count(),
        "suites": Suite.objects.count(),
        "facilities": Facility.objects.count(),
        "data_groups": DataGroup.objects.count(),
        "equipment": Equipment.objects.count(),
        "analysis_types": AnalysisType.objects.count(),
        "units": Unit.objects.count(),
        "inspection_analyses": InspectionAnalysis.objects.count(),
        "parameters": Parameter.objects.count(),
    }

    total_evinces = Evince.objects.count()
    evince_status_counts = Evince.objects.values("status").annotate(
        count=Count("status")
    )
    status_counts = {
        status["status"]: status["count"] for status in evince_status_counts
    }

    return {
        "entity_counts": entity_counts,
        "evince_counts": {
            "total": total_evinces,
            **status_counts,
        },
    }
