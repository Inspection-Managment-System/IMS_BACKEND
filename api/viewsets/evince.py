from datetime import datetime, timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (EvinceSerializer, ParameterSerializer,
                             SimplifiedInspectionResultSerializer)
from ims_backend.utils.helper import get_user_groups
from inspection_management.models import (BusinessUnit, Evince,
                                          InspectionAnalysis, InspectionPoint,
                                          InspectionResult, InspectionTest,
                                          Parameter)
from users.authorization import role_required
from users.models import User
from users.models.audit_history import AuditHistory
from users.models.notification import Notification
from ims_backend.utils.send_email import send_email


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class EvinceViewSet(viewsets.ModelViewSet):
    queryset = Evince.objects.all().order_by("-id")
    serializer_class = EvinceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id", None)
        business_unit = request.query_params.get("business_unit", None)
        site = request.query_params.get("site", None)
        inspection_point = request.query_params.get("inspection_point", None)
        analysis_type = request.query_params.get("analysis_type", None)
        number_of_days = request.query_params.get("number_of_days", None)
        status = request.query_params.get("status", None)
        count = request.query_params.get("count", None)
        managed_by = request.query_params.get("managed_by", None)
        inspected_by = request.query_params.get("inspected_by", None)

        filters = Q()
        if user_id:
            user_data_groups_ids = get_user_groups(user_id)
            if user_data_groups_ids:
                filters &= Q(inspection_point__group__id__in=user_data_groups_ids)
                

        if site:
            filters &= Q(business_unit__site__name=site)

        if business_unit:
            filters &= Q(business_unit__name=business_unit)

        if inspection_point:
            filters &= Q(inspection_point__name=inspection_point)
        if analysis_type:
            filters &= Q(inspection_analyses__analysis_type__name=analysis_type)
        if number_of_days:
            if number_of_days and number_of_days.isdigit():
                days = int(number_of_days)
                target_date = now() - timedelta(days=days)
                filters &= Q(start_date_time__gte=target_date)
        if status:
            filters &= Q(status=status)
        if managed_by:
            filters &= Q(reviewed_by__username=managed_by)
        if inspected_by:
            filters &= Q(assigned_to__username=inspected_by)


        user = User.objects.get(id=user_id)
        user_profile = user.userprofile
        if user_profile.role.name == "Manager":
            filters &= Q(reviewed_by=user)
        elif user_profile.role.name == "Inspector":
            filters &= Q(assigned_to=user)
        
        filtered_queryset = (
            self.queryset.filter(filters).distinct() if filters else self.queryset.all()
        )
        if count and count.lower() == "true":
            
            response_data = {"statuses": [], "dayscount": []}

            status_labels = Evince.get_status_labels()
            for key, value in status_labels.items():
                evinces_count = filtered_queryset.filter(status=key).count()
                response_data["statuses"].append(
                    {"value": value, "label": value, "count": evinces_count}
                )
            time_ranges = [
                {"value": "All time", "label": "All time", "days": None},
                {"value": "5", "label": "Last 5 days", "days": 5},
                {"value": "10", "label": "Last 10 days", "days": 10},
                {"value": "15", "label": "Last 15 days", "days": 15},
                {"value": "30", "label": "Last month", "days": 30},
            ]

            for time_range in time_ranges:
                if time_range["days"] is not None:
                    time_threshold = timezone.now() - timedelta(days=time_range["days"])
                    days_count_queryset = filtered_queryset.filter(
                        start_date_time__gte=time_threshold
                    )
                    days_count = days_count_queryset.count()
                    print(
                        f"Count for {time_range['label']} ({time_range['days']} days): {days_count}"
                    )
                else:
                    days_count = filtered_queryset.count()
                    print(f"Count for All time: {days_count}")

                response_data["dayscount"].append(
                    {
                        "value": time_range["value"],
                        "label": time_range["label"],
                        "count": days_count,
                    }
                )
            
            return Response(response_data)
        
        self.queryset = filtered_queryset
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            print(f"Original data: {data}")
            
            data = self.preprocess_data(data)
            print(f"Preprocessed data: {data}")

            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_create(serializer)
            serializer.instance.save()
            self.create_inspection_tests_and_results(serializer.instance, is_update=False)
        except Exception as e:
            print(f"Error in create method: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        AuditHistory.objects.create(
            user=request.user, action=f"Created evince #{serializer.instance.id}"
        )

        if (
            serializer.instance.assigned_to
            and serializer.instance.assigned_to != request.user
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.assigned_to,
                content=f"You have been assigned to evince #{serializer.instance.id}.",
            )

        if (
            serializer.instance.reviewed_by
            and serializer.instance.reviewed_by != request.user
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.reviewed_by,
                content=f"You have been assigned as reviewer for evince #{serializer.instance.id}.",
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def create_inspection_tests_and_results(self, evince, is_update=False):
        print(f"=== CREATE INSPECTION TESTS AND RESULTS ===")
        print(f"Evince ID: {evince.id}")
        print(f"Is Update: {is_update}")
        print(f"Evince Type: {evince.evince_type}")
        print(f"Caller: {self.__class__.__name__}")
        
        if is_update:
            # For updates, check if we need to recreate
            existing_tests = InspectionTest.objects.filter(evince=evince)
            existing_analyses = set(existing_tests.values_list('inspection_analysis_id', flat=True))
            current_analyses = set(evince.inspection_analyses.values_list('id', flat=True))
            
            # Only recreate if the inspection analyses have actually changed
            if existing_analyses != current_analyses:
                print(f"=== INSPECTION ANALYSES CHANGED - Recreating results ===")
                print(f"Existing analyses: {existing_analyses}")
                print(f"Current analyses: {current_analyses}")
                InspectionTest.objects.filter(evince=evince).delete()
                InspectionResult.objects.filter(evince=evince).delete()
            else:
                print(f"=== INSPECTION ANALYSES UNCHANGED - Preserving existing results ===")
                return  # Don't recreate if analyses haven't changed
        else:
            # For creation, check if results already exist (prevent duplicates)
            existing_results = InspectionResult.objects.filter(evince=evince)
            if existing_results.exists():
                print(f"=== INSPECTION RESULTS ALREADY EXIST - Skipping creation ===")
                print(f"Found {existing_results.count()} existing results")
                return  # Don't create duplicates
        
        print(f"=== CREATING NEW INSPECTION RESULTS ===")
        # Create one inspection test per inspection analysis
        for inspection_analysis in evince.inspection_analyses.all():
            print(f"Creating test for analysis: {inspection_analysis.name}")
            inspection_test = InspectionTest.objects.create(
                evince=evince,
                inspection_analysis=inspection_analysis,
                changed_by=evince.changed_by,
            )
            
            # Create one inspection result per parameter in this inspection analysis
            parameters = Parameter.objects.filter(inspection_analysis=inspection_analysis)
            print(f"Found {parameters.count()} parameters for analysis: {inspection_analysis.name}")
            for parameter in parameters:
                print(f"Creating result for parameter: {parameter.name}")
                InspectionResult.objects.create(
                    evince=evince,
                    inspection_test=inspection_test,
                    changed_by=evince.changed_by,
                )
        
        # Verify final count
        final_results = InspectionResult.objects.filter(evince=evince)
        print(f"=== FINAL RESULT COUNT: {final_results.count()} ===")

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        original_assigned_to = instance.assigned_to
        original_reviewed_by = instance.reviewed_by
        original_status = instance.status

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.create_inspection_tests_and_results(serializer.instance, is_update=True)

        AuditHistory.objects.create(
            user=request.user, action=f"Updated evince #{serializer.instance.id}"
        )

        if (
            original_assigned_to != serializer.instance.assigned_to
            and serializer.instance.assigned_to
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.assigned_to,
                content=f"You have been assigned to evince #{serializer.instance.id}.",
            )

        if (
            original_reviewed_by != serializer.instance.reviewed_by
            and serializer.instance.reviewed_by
        ):
            Notification.objects.create(
                sender=request.user,
                recipient=serializer.instance.reviewed_by,
                content=f"You have been assigned as reviewer for evince #{serializer.instance.id}.",
            )

        return Response(serializer.data)

    def perform_destroy(self, instance):
        evince_id = instance.id

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted evince #{evince_id}"
        )

        if instance.assigned_to and instance.assigned_to != self.request.user:
            Notification.objects.create(
                sender=self.request.user,
                recipient=instance.assigned_to,
                content=f"Evince #{evince_id} that was assigned to you has been deleted.",
            )

        if instance.reviewed_by and instance.reviewed_by != self.request.user:
            Notification.objects.create(
                sender=self.request.user,
                recipient=instance.reviewed_by,
                content=f"Evince #{evince_id} that you were reviewing has been deleted.",
            )

        instance.delete()

    def preprocess_data(self, data):
        if "business_unit" in data:
            business_unit_value = data.get("business_unit")
            # Handle both ID and name
            if isinstance(business_unit_value, (int, str)) and str(business_unit_value).isdigit():
                # It's already an ID
                data["business_unit"] = int(business_unit_value)
            else:
                # It's a name, convert to ID
                try:
                    data["business_unit"] = BusinessUnit.objects.get(name=business_unit_value).id
                except BusinessUnit.DoesNotExist:
                    pass
                    
        if "inspection_point" in data:
            inspection_point_value = data.get("inspection_point")
            # Handle both ID and name
            if isinstance(inspection_point_value, (int, str)) and str(inspection_point_value).isdigit():
                # It's already an ID
                data["inspection_point"] = int(inspection_point_value)
            else:
                # It's a name, convert to ID
                try:
                    data["inspection_point"] = InspectionPoint.objects.get(
                        name=inspection_point_value
                    ).id
                except InspectionPoint.DoesNotExist:
                    pass
                    
        if "inspection_analyses" in data:
            inspection_analysis_values = data.get("inspection_analyses")
            if isinstance(inspection_analysis_values, list):
                for index, inspection_analysis_value in enumerate(inspection_analysis_values):
                    # Handle both ID and name
                    if isinstance(inspection_analysis_value, (int, str)) and str(inspection_analysis_value).isdigit():
                        # It's already an ID
                        data["inspection_analyses"][index] = int(inspection_analysis_value)
                    else:
                        # It's a name, convert to ID
                        try:
                            data["inspection_analyses"][index] = InspectionAnalysis.objects.get(
                                name=inspection_analysis_value
                            ).id
                        except InspectionAnalysis.DoesNotExist:
                            pass

        return data

    @action(detail=True, methods=["get"], url_path="results")
    def get_results(self, request, pk=None):
        """
        Fetch the results and related parameters for a specific Evince.
        """
        inspection_results = InspectionResult.objects.filter(evince_id=pk).select_related(
            "inspection_test__inspection_analysis"
        )
        print(f"=== DEBUG: Fetching results for evince {pk} ===")
        print(f"Found {inspection_results.count()} inspection results")
        for result in inspection_results:
            print(f"Result {result.id}: entered_value='{result.entered_value}', status='{result.status}'")
        
        # Also check the raw database values
        raw_results = InspectionResult.objects.filter(evince_id=pk)
        print(f"=== RAW DATABASE CHECK ===")
        for raw_result in raw_results:
            print(f"Raw Result {raw_result.id}: entered_value='{raw_result.entered_value}', status='{raw_result.status}'")
        
        # Get all parameters for the inspection analyses in this evince
        related_parameters = Parameter.objects.filter(
            inspection_analysis__inspectiontest__evince_id=pk
        ).distinct()

        # Create a list of results with parameter information
        results_with_parameters = []
        for i, result in enumerate(inspection_results):
            # Get the corresponding parameter (assuming one result per parameter)
            parameter = related_parameters[i] if i < len(related_parameters) else None
            
            result_data = {
                "id": result.id,
                "evince": result.evince.id,
                "inspection_test": result.inspection_test.id,
                "inspection_analysis": result.inspection_test.inspection_analysis.name,
                "parameter_name": parameter.name if parameter else "",
                "parameter_description": parameter.description if parameter else "",
                "parameter_unit": parameter.unit.name if parameter and parameter.unit else "",
                "parameter_min_value": parameter.min_value if parameter else None,
                "parameter_max_value": parameter.max_value if parameter else None,
                "parameter_avg_value": parameter.avg_value if parameter else None,
                "parameter_string_value": parameter.string_value if parameter else None,
                "checklist_data_type": parameter.checklist_data_type if parameter else None,
                "entered_value": result.entered_value,
                "comments": result.comments,
                "status": result.status,
                "changed_on": result.changed_on,
                "changed_by": result.changed_by.id,
            }
            print(f"DEBUG: Constructing result_data for {result.id}: entered_value='{result.entered_value}', type={type(result.entered_value)}")
            results_with_parameters.append(result_data)

        return Response(
            {
                "inspection_results": results_with_parameters,
                "related_parameters": ParameterSerializer(related_parameters, many=True).data,
            }
        )

    @action(detail=True, methods=["post"], url_path="status-update")
    def update_status(self, request, pk=None):
        """
        API to update the status of the Evince based on the provided status and update InspectionResult data.
        """
        evince = get_object_or_404(Evince, pk=pk)
        old_status = evince.status
        status_to_update = request.data.get("status")

        if not status_to_update:
            return Response(
                {"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        evince.status = status_to_update

        self.handle_status_update(evince, status_to_update)

        evince.reassigned = True
        evince.save()

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated evince #{evince.id} status from {old_status} to {status_to_update}",
        )

        # --- CRITICAL EMAIL LOGIC (new, does not affect any other logic) ---
        if status_to_update == "ResultsEntered":
            from inspection_management.models import InspectionResult, InspectionTest
            out_of_spec_results = []
            for result in InspectionResult.objects.filter(evince=evince):
                test = result.inspection_test
                param = Parameter.objects.filter(inspection_analysis=test.inspection_analysis).first()
                if param and result.entered_value is not None:
                    try:
                        value = float(result.entered_value)
                        if (param.min_value is not None and value < param.min_value) or (param.max_value is not None and value > param.max_value):
                            out_of_spec_results.append({
                                "parameter": param.name,
                                "entered_value": value,
                                "min_value": param.min_value,
                                "max_value": param.max_value,
                                "comments": result.comments,
                            })
                    except Exception:
                        continue
            if out_of_spec_results:
                # Find manager email (prefer reviewed_by, fallback to business_unit.manager if exists)
                manager_email = None
                manager_name = None
                if hasattr(evince, 'reviewed_by') and evince.reviewed_by and evince.reviewed_by.email:
                    manager_email = evince.reviewed_by.email
                    manager_name = evince.reviewed_by.username
                elif hasattr(evince.business_unit, 'manager') and evince.business_unit.manager and evince.business_unit.manager.email:
                    manager_email = evince.business_unit.manager.email
                    manager_name = evince.business_unit.manager.username
                if manager_email:
                    subject = f"URGENT ALERT: CRITICAL OUT-OF-SPEC RESULTS - Evince #{evince.id}"
                    
                    # Simple text content
                    text_content = f"""
CRITICAL ALERT: OUT-OF-SPECIFICATION INSPECTION RESULTS

Evince #{evince.id} has CRITICAL results that are OUT OF SPECIFICATION!

This requires IMMEDIATE ATTENTION and URGENT REVIEW.

OUT-OF-SPEC PARAMETERS:
"""
                    for r in out_of_spec_results:
                        text_content += f"Parameter: {r['parameter']} | Value: {r['entered_value']} | Min: {r['min_value']} | Max: {r['max_value']} | Comments: {r['comments']}\n"
                    
                    text_content += """

ACTION REQUIRED: Please review these results IMMEDIATELY!
These out-of-spec values indicate potential quality issues that need urgent attention.
Failure to address these issues may result in compliance violations.

This is a HIGH PRIORITY alert that requires your immediate response.
"""
                    
                    # Simple HTML content
                    html_content = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 20px;">
                        <div style="background: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                            <h1 style="margin: 0; font-size: 24px;">CRITICAL ALERT</h1>
                            <p style="margin: 10px 0 0 0;">OUT-OF-SPECIFICATION INSPECTION RESULTS DETECTED</p>
                        </div>
                        
                        <div style="background: white; padding: 20px; border-radius: 0 0 10px 10px;">
                            <div style="background: #fef2f2; border: 2px solid #dc2626; padding: 15px; margin: 20px 0; border-radius: 5px;">
                                <h2 style="color: #dc2626; margin-top: 0;">CRITICAL QUALITY ISSUE DETECTED</h2>
                                <p style="font-weight: bold; color: #dc2626;">
                                    Evince #{evince.id} has results OUT OF SPECIFICATION that require IMMEDIATE attention!
                                </p>
                            </div>
                            
                            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                                <thead>
                                    <tr style="background: #dc2626; color: white;">
                                        <th style="padding: 10px; text-align: left;">Parameter</th>
                                        <th style="padding: 10px; text-align: left;">Value</th>
                                        <th style="padding: 10px; text-align: left;">Spec Range</th>
                                        <th style="padding: 10px; text-align: left;">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                    """
                    
                    for r in out_of_spec_results:
                        html_content += f"""
                                    <tr style="border-bottom: 1px solid #e5e7eb;">
                                        <td style="padding: 10px;"><strong>{r['parameter']}</strong></td>
                                        <td style="padding: 10px; color: #dc2626; font-weight: bold;">{r['entered_value']}</td>
                                        <td style="padding: 10px;">{r['min_value']} - {r['max_value']}</td>
                                        <td style="padding: 10px; color: #dc2626; font-weight: bold;">OUT OF SPEC</td>
                                    </tr>
                        """
                    
                    html_content += """
                                </tbody>
                            </table>
                            
                            <div style="background: #dc2626; color: white; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                                <strong>IMMEDIATE ACTION REQUIRED</strong>
                            </div>
                            
                            <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                                <h3 style="color: #dc2626; margin-top: 0;">URGENT IMPLICATIONS:</h3>
                                <ul>
                                    <li><strong>Quality Control Issue:</strong> These out-of-spec values indicate potential quality problems</li>
                                    <li><strong>Compliance Risk:</strong> May violate regulatory or industry standards</li>
                                    <li><strong>Safety Concern:</strong> Could impact product safety or performance</li>
                                </ul>
                            </div>
                            
                            <div style="background: #1f2937; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <h3 style="margin-top: 0;">REQUIRED ACTIONS:</h3>
                                <ol>
                                    <li><strong>Immediate Review:</strong> Examine these results within the next 2 hours</li>
                                    <li><strong>Root Cause Analysis:</strong> Investigate why these values are out of specification</li>
                                    <li><strong>Corrective Action:</strong> Implement immediate corrective measures</li>
                                </ol>
                            </div>
                            
                            <p style="text-align: center; font-weight: bold; color: #dc2626; font-size: 16px;">
                                This alert requires your IMMEDIATE attention - Do not delay!
                            </p>
                        </div>
                        
                        <div style="background: #1f2937; color: white; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px;">
                            <p><strong>Inspection Management System</strong></p>
                            <p>This is an automated critical alert. Please respond immediately.</p>
                        </div>
                    </div>
                    """
                    try:
                        send_email(subject, [manager_email], text_content, html_content)
                        
                        # Also create a notification in the system for immediate visibility
                        Notification.objects.create(
                            sender=request.user,
                            recipient=evince.reviewed_by if evince.reviewed_by else evince.business_unit.manager,
                            content=f"CRITICAL ALERT: Evince #{evince.id} has {len(out_of_spec_results)} out-of-specification results that require IMMEDIATE attention! Check your email for details.",
                        )
                    except Exception as e:
                        print(f"Failed to send critical email: {e}")
        # --- END CRITICAL EMAIL LOGIC ---

        self.send_status_update_notifications(
            evince, old_status, status_to_update, request.user
        )

        return Response(
            {"message": f"Evince status updated to {status_to_update}."},
            status=status.HTTP_200_OK,
        )

    def send_status_update_notifications(self, evince, old_status, new_status, user):

        if new_status == "ResultsEntered":
            if evince.reviewed_by and evince.reviewed_by != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.reviewed_by,
                    content=f"Results have been entered for evince #{evince.id} and are ready for your review.",
                )

        elif new_status == "Rejected":
            if evince.assigned_to and evince.assigned_to != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.assigned_to,
                    content=f"Evince #{evince.id} has been rejected and requires your attention.",
                )

        elif new_status == "Reassigned":
            if evince.assigned_to and evince.assigned_to != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.assigned_to,
                    content=f"Evince #{evince.id} has been reassigned to you and requires your attention.",
                )

        elif new_status == "Approved":
            if evince.assigned_to and evince.assigned_to != user:
                Notification.objects.create(
                    sender=user,
                    recipient=evince.assigned_to,
                    content=f"Evince #{evince.id} has been approved. Good job!",
                )

    def handle_status_update(self, evince, status_to_update):
        """
        Handles the status update and relevant InspectionResult modifications.
        """
        if status_to_update == "ResultsEntered":
            self.set_results_entered(evince)
        elif status_to_update == "Rejected":
            self.set_rejected(evince)
        elif status_to_update == "Reassigned":
            self.set_reassigned(evince)
        elif status_to_update == "Approved":
            self.set_approved(evince)

    def set_results_entered(self, evince):
        InspectionResult.objects.filter(evince=evince).update(status="Completed")

    def set_rejected(self, evince):
        pass

    def set_reassigned(self, evince):
        inspection_test_results = InspectionResult.objects.filter(evince=evince)
        for result in inspection_test_results:
            result.previous_value = result.entered_value
            result.status = "Incomplete"
            result.save()

    def set_approved(self, evince):
        pass

    # HSE Risk Management Methods
    def get_queryset(self):
        """Override to filter by evince type"""
        queryset = super().get_queryset()
        evince_type = self.request.query_params.get('evince_type')
        
        if evince_type == 'hse_risk_management':
            return queryset.filter(evince_type='hse_risk_management')
        elif evince_type:
            return queryset.filter(evince_type=evince_type)
        
        return queryset

    @action(detail=False, methods=['get'], url_path='hse-risk-dashboard')
    def hse_risk_dashboard(self, request):
        """Get HSE Risk Management dashboard statistics"""
        try:
            from api.services.hse_risk_evince_service import HSERiskEvinceService
            from api.serializers.hse_risk_serializers import HSERiskDashboardStatsSerializer
            
            stats = HSERiskEvinceService.get_hse_risk_dashboard_stats()
            serializer = HSERiskDashboardStatsSerializer(stats)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='hse-risk-create')
    def hse_risk_create(self, request):
        """Create HSE Risk Management evince"""
        try:
            from api.serializers.hse_risk_serializers import HSERiskEvinceCreateSerializer
            
            serializer = HSERiskEvinceCreateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                evince = serializer.save()
                from api.serializers.hse_risk_serializers import HSERiskEvinceSerializer
                response_serializer = HSERiskEvinceSerializer(evince)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='hse-risk-inspector-review')
    def hse_risk_inspector_review(self, request, pk=None):
        """Inspector review of HSE Risk evince"""
        try:
            from api.services.hse_risk_evince_service import HSERiskEvinceService
            from api.serializers.hse_risk_serializers import HSERiskInspectorReviewSerializer
            
            evince = self.get_object()
            if evince.evince_type != 'hse_risk_management':
                return Response({'error': 'Invalid evince type'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = HSERiskInspectorReviewSerializer(data=request.data)
            if serializer.is_valid():
                risk_assessment_data = serializer.validated_data['risk_assessment']
                risk_assessment_data['notes'] = serializer.validated_data.get('comments', '')
                
                updated_evince = HSERiskEvinceService.inspector_review(
                    evince, request.user, risk_assessment_data
                )
                
                from api.serializers.hse_risk_serializers import HSERiskEvinceSerializer
                response_serializer = HSERiskEvinceSerializer(updated_evince)
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='hse-risk-manager-assignment')
    def hse_risk_manager_assignment(self, request, pk=None):
        """Manager assignment of HSE Risk evince"""
        try:
            from api.services.hse_risk_evince_service import HSERiskEvinceService
            from api.serializers.hse_risk_serializers import HSERiskManagerAssignmentSerializer
            
            evince = self.get_object()
            if evince.evince_type != 'hse_risk_management':
                return Response({'error': 'Invalid evince type'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = HSERiskManagerAssignmentSerializer(data=request.data)
            if serializer.is_valid():
                assignment_data = serializer.validated_data
                
                updated_evince = HSERiskEvinceService.manager_assignment(
                    evince, request.user, assignment_data
                )
                
                from api.serializers.hse_risk_serializers import HSERiskEvinceSerializer
                response_serializer = HSERiskEvinceSerializer(updated_evince)
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='hse-risk-lims-completion')
    def hse_risk_lims_completion(self, request, pk=None):
        """LIMS completion callback"""
        try:
            from api.services.hse_risk_evince_service import HSERiskEvinceService
            from api.serializers.hse_risk_serializers import HSERiskLIMSCompletionSerializer
            
            evince = self.get_object()
            if evince.evince_type != 'hse_risk_management':
                return Response({'error': 'Invalid evince type'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = HSERiskLIMSCompletionSerializer(data=request.data)
            if serializer.is_valid():
                lims_data = serializer.validated_data
                
                updated_evince = HSERiskEvinceService.lims_completion(evince, lims_data)
                
                from api.serializers.hse_risk_serializers import HSERiskEvinceSerializer
                response_serializer = HSERiskEvinceSerializer(updated_evince)
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='hse-risk-manager-approval')
    def hse_risk_manager_approval(self, request, pk=None):
        """Manager approval of LIMS results"""
        try:
            from api.services.hse_risk_evince_service import HSERiskEvinceService
            from api.serializers.hse_risk_serializers import HSERiskManagerApprovalSerializer
            
            evince = self.get_object()
            if evince.evince_type != 'hse_risk_management':
                return Response({'error': 'Invalid evince type'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = HSERiskManagerApprovalSerializer(data=request.data)
            if serializer.is_valid():
                approval_data = serializer.validated_data
                
                updated_evince = HSERiskEvinceService.manager_approval(
                    evince, request.user, approval_data
                )
                
                from api.serializers.hse_risk_serializers import HSERiskEvinceSerializer
                response_serializer = HSERiskEvinceSerializer(updated_evince)
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='hse-risk-workflow-states')
    def hse_risk_workflow_states(self, request, pk=None):
        """Get HSE Risk workflow states and transitions"""
        try:
            from api.services.hse_risk_evince_service import HSERiskEvinceService
            
            evince = self.get_object()
            if evince.evince_type != 'hse_risk_management':
                return Response({'error': 'Invalid evince type'}, status=status.HTTP_400_BAD_REQUEST)
            
            workflow_data = {
                'current_status': evince.status,
                'available_transitions': HSERiskEvinceService.HSE_RISK_TRANSITIONS.get(evince.status, []),
                'workflow_states': HSERiskEvinceService.HSE_RISK_WORKFLOW_STATES
            }
            
            return Response(workflow_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)