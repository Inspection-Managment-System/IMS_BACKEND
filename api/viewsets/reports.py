from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.services.reports import (fetch_all_equipment,
                                  fetch_analysis_type_report,
                                  fetch_business_units_and_evinces,
                                  fetch_certificate_of_inspection,
                                  fetch_equipment_requiring_calibration,
                                  fetch_evince_details,
                                  fetch_generic_facility_functionality_report,
                                  fetch_inspection_data,
                                  fetch_inspection_result_trend_report,
                                  fetch_overdue_evinces,
                                  fetch_single_equipment_report,
                                  fetch_summary_report, get_inspectors_list,
                                  single_inspector_performance)
from users.models import User, UserProfile
from users.models.audit_history import AuditHistory


class IMSReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="summary")
    def summary_report(self, request):
        try:
            summary_data = fetch_summary_report()

            AuditHistory.objects.create(
                user=request.user,
                action="Generated summary report"
            )

            return Response(summary_data)
        except Exception as e:
            raise ValidationError({"error": str(e)})

    @action(detail=False, methods=["get"], url_path="evince_summary")
    def evince_summary(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        business_unit_id = request.query_params.get("business_unit")

        try:
            business_unit_data = fetch_inspection_data(
                start_date, end_date, business_unit_id
            )

            AuditHistory.objects.create(
                user=request.user,
                action=f"Retrieved evince summary for business unit: {business_unit_id}, period: {start_date} to {end_date}"
            )

            return Response({"business_units": business_unit_data})
        except ValueError as e:
            raise ValidationError({"error": str(e)})

    @action(detail=False, methods=["get"], url_path="facility_functionality")
    def facility_functionality(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        report_data = fetch_generic_facility_functionality_report(start_date, end_date)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Generated facility functionality report for period: {start_date} to {end_date}"
        )

        return Response({"facility_summary": report_data})

    @action(detail=False, methods=["get"], url_path="list_inspectors")
    def list_inspectors(self, request):
        manager_id = request.query_params.get("user")

        if not manager_id:
            return Response({"error": "Manager ID is required."}, status=400)

        try:
            inspectors = get_inspectors_list(manager_id)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Listed inspectors for manager: {manager_id}"
            )

            return Response(inspectors, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="inspector_performance")
    def inspector_performance_report(self, request):
        user = request.query_params.get("user")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not user:
            raise ValidationError({"error": "Inspector ID is required."})

        try:
            performance_data = single_inspector_performance(user, start_date, end_date)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Generated performance report for inspector: {user}, period: {start_date} to {end_date}"
            )

            return Response(performance_data)
        except ValueError as ve:
            raise ValidationError({"error": str(ve)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="analysis_type_report")
    def analysis_type_report(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            report_data = fetch_analysis_type_report(start_date, end_date)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Generated analysis type report for period: {start_date} to {end_date}"
            )

            return Response(report_data)
        except ValueError as e:
            raise ValidationError({"error": str(e)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="inspection_result_trend")
    def inspection_result_trend(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        anomaly_threshold = request.query_params.get("anomaly_threshold", 20)

        try:
            report_data = fetch_inspection_result_trend_report(
                start_date=start_date,
                end_date=end_date,
                anomaly_threshold=int(anomaly_threshold),
            )

            AuditHistory.objects.create(
                user=request.user,
                action=f"Generated inspection result trend report for period: {start_date} to {end_date}"
            )

            return Response(report_data)
        except ValueError as ve:
            raise ValidationError({"error": str(ve)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="business_units_and_evinces")
    def get_business_units_and_evinces(self, request):
        user = request.user
        business_unit_id = request.query_params.get("business_unit_id")

        try:
            data = fetch_business_units_and_evinces(user, business_unit_id)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Retrieved business units and evinces data for business unit: {business_unit_id}"
            )

            return Response(data)
        except ValueError as e:
            raise ValidationError({"error": str(e)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="certificate_of_inspection")
    def get_certificate_of_inspection(self, request):
        evince_id = request.query_params.get("evince_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not evince_id:
            raise ValidationError({"error": "Evince ID is required."})

        try:
            data = fetch_certificate_of_inspection(evince_id, start_date, end_date)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Generated certificate of inspection for evince: {evince_id}, period: {start_date} to {end_date}"
            )

            return Response(data)
        except ValueError as e:
            raise ValidationError({"error": str(e)})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="overdue_evince_data")
    def evince_data(self, request):
        evince_id = request.query_params.get("evince_id")
        inspector_id = request.query_params.get("inspector_id")
        business_unit_id = request.query_params.get("business_unit_id")

        if evince_id:
            try:
                data = fetch_evince_details(evince_id)

                AuditHistory.objects.create(
                    user=request.user,
                    action=f"Retrieved details for evince: {evince_id}"
                )

                return Response({"evince_details": data})
            except Exception as e:
                return Response({"error": str(e)}, status=500)

        try:
            data = fetch_overdue_evinces(inspector_id, business_unit_id)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Retrieved overdue evinces for inspector: {inspector_id}, business unit: {business_unit_id}"
            )

            return Response({"overdue_evinces": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="all_equipment")
    def all_equipment(self, request):
        user_id = request.query_params.get("user")
        if not user_id:
            raise ValidationError({"error": "User parameter is required."})
        try:
            data = fetch_all_equipment(user_id)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Retrieved all equipment data for user: {user_id}"
            )

            return Response({"equipment": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="equipment_requiring_calibration")
    def equipment_requiring_calibration(self, request):
        user_id = request.query_params.get("user")
        if not user_id:
            raise ValidationError({"error": "User parameter is required."})
        try:
            data = fetch_equipment_requiring_calibration(user_id)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Retrieved equipment requiring calibration for user: {user_id}"
            )

            return Response({"equipment": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="single_equipment")
    def single_equipment(self, request):
        user_id = request.query_params.get("user")
        equipment_id = request.query_params.get("equipment_id")
        if not user_id or not equipment_id:
            raise ValidationError(
                {"error": "User and equipment_id parameters are required."}
            )
        try:
            data = fetch_single_equipment_report(user_id, equipment_id)

            AuditHistory.objects.create(
                user=request.user,
                action=f"Retrieved single equipment report for user: {user_id}, equipment: {equipment_id}"
            )

            return Response({"equipment_details": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="plant_performance")
    def plant_performance(self, request):
        try:
            data = {
                "report_name": "Monthly Plant Performance Report",
                "generated_on": "2024-12-08",
                "plant_name": "Green Valley Power Plant",
                "reporting_period": "November 2024",
                "sections": [
                ]
            }

            AuditHistory.objects.create(
                user=request.user,
                action="Generated plant performance report"
            )

            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="oil_and_gas_performance")
    def oil_and_gas_performance(self, request):
        try:
            data = {
                "report_name": "Quarterly Well Performance Analysis",
            }

            AuditHistory.objects.create(
                user=request.user,
                action="Generated oil and gas performance report"
            )

            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="factory_quality_assurance")
    def factory_quality_assurance(self, request):
        try:
            data = {
                "report_name": "Weekly Quality Assurance Summary",
            }

            AuditHistory.objects.create(
                user=request.user,
                action="Generated factory quality assurance report"
            )

            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="construction_progress")
    def construction_progress(self, request):
        try:
            data = {
                "report_name": "Monthly Construction Progress Report",
            }

            AuditHistory.objects.create(
                user=request.user,
                action="Generated construction progress report"
            )

            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="hospital_equipment_utilization")
    def hospital_equipment_utilization(self, request):
        try:
            data = {
                "report_name": "Monthly Hospital Equipment Utilization",
            }

            AuditHistory.objects.create(
                user=request.user,
                action="Generated hospital equipment utilization report"
            )

            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)