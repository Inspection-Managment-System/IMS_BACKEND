from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.services.reports import (
    fetch_analysis_type_report,
    fetch_generic_facility_functionality_report,
    fetch_inspection_data,
    fetch_inspection_result_trend_report,
    fetch_summary_report,
    get_inspectors_list,
    single_inspector_performance,
)
from users.models import User, UserProfile


class IMSReportViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="summary")
    def summary_report(self, request):
        """
        Fetch a detailed summary report.
        """
        try:
            # Fetch summary report data
            summary_data = fetch_summary_report()
            return Response(summary_data)
        except Exception as e:
            raise ValidationError({"error": str(e)})

    @action(detail=False, methods=["get"], url_path="evince_summary")
    def evince_summary(self, request):

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        business_unit_id = request.query_params.get("business_unit")

        try:
            # Fetch data using the service function
            business_unit_data = fetch_inspection_data(
                start_date, end_date, business_unit_id
            )
            return Response({"business_units": business_unit_data})
        except ValueError as e:
            raise ValidationError({"error": str(e)})

    @action(detail=False, methods=["get"], url_path="facility_functionality")
    def facility_functionality(self, request):

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Fetch the report data using the service function
        report_data = fetch_generic_facility_functionality_report(start_date, end_date)

        return Response({"facility_summary": report_data})

    @action(detail=False, methods=["get"], url_path="list_inspectors")
    def list_inspectors(self, request):
        manager_id = request.query_params.get("user")

        if not manager_id:
            return Response({"error": "Manager ID is required."}, status=400)

        try:
            inspectors = get_inspectors_list(manager_id)
            return Response(inspectors, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="inspector_performance")
    def inspector_performance_report(self, request):
        """
        Fetch performance metrics for a specific inspector.
        """
        user = request.query_params.get("user")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not user:
            raise ValidationError({"error": "Inspector ID is required."})

        try:
            performance_data = single_inspector_performance(user, start_date, end_date)
            return Response(performance_data)
        except ValueError as ve:
            raise ValidationError({"error": str(ve)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="analysis_type_report")
    def analysis_type_report(self, request):
        """
        Fetch a report summarizing the types of analyses performed and their outcomes.
        """
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            report_data = fetch_analysis_type_report(start_date, end_date)
            return Response(report_data)
        except ValueError as e:
            raise ValidationError({"error": str(e)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="inspection_result_trend")
    def inspection_result_trend(self, request):
        """
        API endpoint for fetching trends in inspection results.
        """
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        anomaly_threshold = request.query_params.get("anomaly_threshold", 20)

        try:
            # Fetch trend report data
            report_data = fetch_inspection_result_trend_report(
                start_date=start_date,
                end_date=end_date,
                anomaly_threshold=int(anomaly_threshold),
            )
            return Response(report_data)
        except ValueError as ve:
            raise ValidationError({"error": str(ve)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
