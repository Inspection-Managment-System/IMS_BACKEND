from datetime import datetime

from django.db.models import (Avg, Count, ExpressionWrapper, F, FloatField,
                              Max, Min, Q)
from django.db.models.functions import TruncMonth
from django.utils.timezone import make_aware

from inspection_management.models import Evince, InspectionResult


def fetch_inspection_result_trend_report(
    start_date=None, end_date=None, anomaly_threshold=20
):

    if start_date:
        start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))

    approved_evinces = Evince.objects.filter(
        status="Approved", start_date_time__gte=start_date, end_date_time__lte=end_date
    )

    inspection_results = InspectionResult.objects.filter(evince__in=approved_evinces)

    trends = (
        inspection_results.values(
            "evince__business_unit__name",
            "inspection_test__inspection_analysis__name",
        )
        .annotate(
            avg_value=Avg("entered_value"),
            min_value=Min("entered_value"),
            max_value=Max("entered_value"),
            total_count=Count("id"),
        )
        .order_by(
            "evince__business_unit__name", "inspection_test__inspection_analysis__name"
        )
    )

    anomalies = (
        inspection_results.annotate(
            difference=ExpressionWrapper(
                F("entered_value") - F("previous_value"), output_field=FloatField()
            )
        )
        .filter(difference__gte=anomaly_threshold)
        .values(
            "inspection_test__inspection_analysis__name",
            "entered_value",
            "previous_value",
            "difference",
            "evince__business_unit__name",
            "changed_on",
        )
    )

    trend_data = {}
    for trend in trends:
        business_unit = trend["evince__business_unit__name"]
        analysis_name = trend["inspection_test__inspection_analysis__name"]

        if business_unit not in trend_data:
            trend_data[business_unit] = []

        trend_data[business_unit].append(
            {
                "analysis_name": analysis_name,
                "avg_value": trend["avg_value"],
                "min_value": trend["min_value"],
                "max_value": trend["max_value"],
                "total_count": trend["total_count"],
            }
        )

    anomaly_data = [
        {
            "business_unit": anomaly["evince__business_unit__name"],
            "analysis_name": anomaly["inspection_test__inspection_analysis__name"],
            "entered_value": anomaly["entered_value"],
            "previous_value": anomaly["previous_value"],
            "difference": anomaly["difference"],
            "date": anomaly["changed_on"],
        }
        for anomaly in anomalies
    ]

    return {
        "trends": trend_data,
        "anomalies": anomaly_data,
    }
