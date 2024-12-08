from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.services.reports import (fetch_analysis_type_report,
                                  fetch_business_units_and_evinces,
                                  fetch_certificate_of_inspection,
                                  fetch_generic_facility_functionality_report,
                                  fetch_inspection_data,
                                  fetch_inspection_result_trend_report,
                                  fetch_summary_report, get_inspectors_list,
                                  single_inspector_performance,
                                  fetch_evince_details,
                                  fetch_overdue_evinces,
                                  fetch_all_equipment,
                                  fetch_equipment_requiring_calibration,
                                  fetch_single_equipment_report)
from users.models import User, UserProfile


class IMSReportViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="summary")
    def summary_report(self, request):

        try:
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

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        anomaly_threshold = request.query_params.get("anomaly_threshold", 20)

        try:
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

    @action(detail=False, methods=["get"], url_path="business_units_and_evinces")
    def get_business_units_and_evinces(self, request):
        user = request.user
        business_unit_id = request.query_params.get("business_unit_id")

        try:
            data = fetch_business_units_and_evinces(user, business_unit_id)
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
                return Response({"evince_details": data})
            except Exception as e:
                return Response({"error": str(e)}, status=500)

        try:
            data = fetch_overdue_evinces(inspector_id, business_unit_id)
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
            return Response({"equipment": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="single_equipment")
    def single_equipment(self, request):
        user_id = request.query_params.get("user")
        equipment_id = request.query_params.get("equipment_id")
        if not user_id or not equipment_id:
            raise ValidationError({"error": "User and equipment_id parameters are required."})
        try:
            data = fetch_single_equipment_report(user_id, equipment_id)
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
                    {
                        "section_name": "Operational Efficiency",
                        "total_output": "150,000 MW",
                        "operating_hours": "720 hours",
                        "efficiency": "92%",
                        "downtime": {
                            "total_downtime": "12 hours",
                            "causes": [
                                {"cause": "Equipment Failure", "duration": "8 hours"},
                                {"cause": "Scheduled Maintenance", "duration": "4 hours"}
                            ]
                        },
                        "recommendations": "Invest in predictive maintenance tools to reduce unplanned downtime."
                    },
                    {
                        "section_name": "Maintenance Activities",
                        "total_maintenance_tasks": 45,
                        "completed_tasks": 42,
                        "overdue_tasks": 3,
                        "cost_analysis": {
                            "labor_costs": "$10,000",
                            "parts_costs": "$8,500",
                            "total_costs": "$18,500"
                        },
                        "recommendations": "Streamline task scheduling to prevent delays in critical maintenance."
                    },
                    {
                        "section_name": "Environmental Compliance",
                        "emission_levels": "Within regulatory limits",
                        "energy_consumption": "1,500,000 kWh",
                        "recommendations": "Optimize boiler efficiency to reduce fuel consumption."
                    }
                ]
            }
            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    

    @action(detail=False, methods=["get"], url_path="oil_and_gas_performance")
    def oil_and_gas_performance(self, request):
        try:
            data = {
                "report_name": "Quarterly Well Performance Analysis",
                "generated_on": "2024-12-08",
                "company_name": "Alpha Energy",
                "reporting_period": "Q3 2024",
                "total_wells": 50,
                "sections": [
                    {
                        "section_name": "Production Overview",
                        "total_production": "3,000,000 barrels",
                        "average_production_per_well": "60,000 barrels",
                        "non_operational_wells": 5,
                        "recommendations": "Reassess the production strategy for underperforming wells."
                    },
                    {
                        "section_name": "Incident Reports",
                        "incidents": [
                            {"date": "2024-08-15", "type": "Oil Leak", "impact": "Minor", "resolution_time": "6 hours"},
                            {"date": "2024-09-20", "type": "Valve Failure", "impact": "Moderate", "resolution_time": "12 hours"}
                        ],
                        "recommendations": "Upgrade equipment monitoring systems to reduce incidents."
                    },
                    {
                        "section_name": "Environmental Compliance",
                        "compliance_rate": "98%",
                        "violations": [
                            {"violation": "Excess flaring", "fine": "$5,000"}
                        ],
                        "recommendations": "Implement stricter emission control measures."
                    }
                ]
            }
            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)



    @action(detail=False, methods=["get"], url_path="factory_quality_assurance")
    def factory_quality_assurance(self, request):
        try:
            data = {
                "report_name": "Weekly Quality Assurance Summary",
                "generated_on": "2024-12-08",
                "factory_name": "Pinnacle Manufacturing",
                "reporting_period": "Week of December 1, 2024",
                "sections": [
                    {
                        "section_name": "Production Output",
                        "total_units_produced": 10000,
                        "defective_units": 250,
                        "defect_rate": "2.5%",
                        "top_defect_causes": [
                            {"cause": "Machine Misalignment", "percentage": "50%"},
                            {"cause": "Raw Material Quality", "percentage": "30%"}
                        ],
                        "recommendations": "Enhance material quality checks and conduct equipment recalibration."
                    },
                    {
                        "section_name": "Compliance Status",
                        "inspections_conducted": 5,
                        "compliance_rate": "100%",
                        "recommendations": "Continue adhering to ISO 9001 standards."
                    },
                    {
                        "section_name": "Employee Training",
                        "trained_employees": 120,
                        "total_employees": 150,
                        "training_compliance": "80%",
                        "recommendations": "Expand training programs to cover 100% of the workforce."
                    }
                ]
            }
            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="construction_progress")
    def construction_progress(self, request):
        try:
            data = {
                "report_name": "Monthly Construction Progress Report",
                "generated_on": "2024-12-08",
                "project_name": "Downtown Skyscraper Project",
                "reporting_period": "November 2024",
                "sections": [
                    {
                        "section_name": "Progress Summary",
                        "completion_percentage": "75%",
                        "tasks_completed": 150,
                        "tasks_remaining": 50,
                        "recommendations": "Allocate additional resources to accelerate structural work."
                    },
                    {
                        "section_name": "Budget Analysis",
                        "total_budget": "$50,000,000",
                        "spent_to_date": "$38,000,000",
                        "remaining_budget": "$12,000,000",
                        "overruns": "$1,500,000",
                        "recommendations": "Tighten procurement processes to minimize cost overruns."
                    },
                    {
                        "section_name": "Safety Incidents",
                        "incidents_reported": 2,
                        "details": [
                            {"date": "2024-11-12", "type": "Fall Injury", "severity": "Moderate"},
                            {"date": "2024-11-20", "type": "Equipment Malfunction", "severity": "Minor"}
                        ],
                        "recommendations": "Conduct additional safety drills and equipment inspections."
                    }
                ]
            }
            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


    @action(detail=False, methods=["get"], url_path="hospital_equipment_utilization")
    def hospital_equipment_utilization(self, request):
        try:
            data = {
                "report_name": "Monthly Hospital Equipment Utilization",
                "generated_on": "2024-12-08",
                "hospital_name": "City General Hospital",
                "reporting_period": "November 2024",
                "sections": [
                    {
                        "section_name": "Equipment Utilization",
                        "total_equipment": 200,
                        "utilization_rate": "85%",
                        "underutilized_equipment": 15,
                        "recommendations": "Relocate underutilized equipment to high-demand departments."
                    },
                    {
                        "section_name": "Maintenance Overview",
                        "scheduled_maintenance": 30,
                        "completed_maintenance": 28,
                        "pending_maintenance": 2,
                        "recommendations": "Streamline vendor coordination to ensure timely maintenance."
                    },
                    {
                        "section_name": "Critical Incidents",
                        "incidents_reported": 1,
                        "details": [
                            {"date": "2024-11-15", "type": "Ventilator Failure", "impact": "Critical"}
                        ],
                        "recommendations": "Upgrade ventilator monitoring systems to avoid future incidents."
                    }
                ]
            }
            return Response({"report": data})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
