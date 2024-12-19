from datetime import datetime

from django.db.models import Count, Q
from django.utils.timezone import make_aware

from inspection_management.models import AnalysisType, InspectionResult


def fetch_analysis_type_report(start_date=None, end_date=None):

    if start_date:
        start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))

    filters = {}
    if start_date:
        filters["changed_on__gte"] = start_date
    if end_date:
        filters["changed_on__lte"] = end_date

    inspection_results = InspectionResult.objects.filter(**filters)

    analysis_data = AnalysisType.objects.annotate(
        total_performed=Count(
            "inspectionanalysis__inspectiontest__inspectionresult",
            filter=Q(
                inspectionanalysis__inspectiontest__inspectionresult__in=inspection_results
            ),
        ),
        pass_count=Count(
            "inspectionanalysis__inspectiontest__inspectionresult",
            filter=Q(
                inspectionanalysis__inspectiontest__inspectionresult__status="Completed",
                inspectionanalysis__inspectiontest__inspectionresult__in=inspection_results,
            ),
        ),
        fail_count=Count(
            "inspectionanalysis__inspectiontest__inspectionresult",
            filter=Q(
                inspectionanalysis__inspectiontest__inspectionresult__status="Incomplete",
                inspectionanalysis__inspectiontest__inspectionresult__in=inspection_results,
            ),
        ),
    ).filter(total_performed__gt=0)

    report_summary = []
    for analysis in analysis_data:
        total = analysis.total_performed
        passed = analysis.pass_count
        failed = analysis.fail_count

        report_summary.append(
            {
                "analysis_name": analysis.name,
                "description": analysis.description,
                "total_performed": total,
                "pass_count": passed,
                "fail_count": failed,
                "pass_rate": round((passed / total) * 100, 2) if total > 0 else 0,
                "fail_rate": round((failed / total) * 100, 2) if total > 0 else 0,
            }
        )

    trends = (
        inspection_results.values(
            "inspection_test__inspection_analysis__analysis_type__name",
            "changed_on__date",
        )
        .annotate(total=Count("id"))
        .order_by("changed_on__date")
    )

    trend_data = {}
    for trend in trends:
        analysis_name = trend[
            "inspection_test__inspection_analysis__analysis_type__name"
        ]
        if analysis_name not in trend_data:
            trend_data[analysis_name] = []
        trend_data[analysis_name].append(
            {
                "date": trend["changed_on__date"],
                "total": trend["total"],
            }
        )

    return {
        "summary": report_summary,
        "trends": trend_data,
    }
