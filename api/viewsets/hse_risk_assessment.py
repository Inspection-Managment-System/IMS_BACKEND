from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from inspection_management.models import Evince, BusinessUnit, InspectionAnalysis, InspectionPoint
from api.serializers.hse_risk_assessment import (
    HSERiskAssessmentSerializer,
    HSERiskAssessmentCreateSerializer,
    HSERiskAssessmentUpdateSerializer
)
from api.viewsets.evince import EvinceViewSet


class HSERiskAssessmentViewSet(EvinceViewSet):
    """ViewSet for HSE Risk Assessment workflow"""
    
    queryset = Evince.objects.filter(evince_type='hse_risk_management')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return HSERiskAssessmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return HSERiskAssessmentUpdateSerializer
        return HSERiskAssessmentSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list method to handle HSE-specific filtering without user_id dependency"""
        user = request.user
        queryset = self.queryset
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by risk level if provided
        risk_level = request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(hse_risk_level=risk_level)
        
        # Filter by assigned user if provided
        assigned_to = request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter by mitigation department if provided
        mitigation_dept = request.query_params.get('mitigation_department')
        if mitigation_dept:
            queryset = queryset.filter(hse_mitigation_department_id=mitigation_dept)
        
        # Role-based filtering
        if hasattr(user, 'userprofile') and user.userprofile.role:
            role = user.userprofile.role.name.upper()
            if role == 'ADMIN':
                # Admin can see all HSE risk assessments
                pass
            elif role == 'MANAGER':
                # Manager can see assessments for their data groups
                user_data_groups = user.userprofile.data_groups.all()
                queryset = queryset.filter(
                    Q(business_unit__group__in=user_data_groups) |
                    Q(hse_mitigation_department__group__in=user_data_groups)
                )
            elif role == 'INSPECTOR':
                # Inspector can see assessments assigned to them
                queryset = queryset.filter(
                    Q(assigned_to=user) |
                    Q(hse_mitigation_assigned_to=user)
                )
            else:
                # Other users can only see assessments assigned to them
                queryset = queryset.filter(
                    Q(assigned_to=user) |
                    Q(hse_mitigation_assigned_to=user)
                )
        
        # Apply pagination and return response
        page = self.paginate_queryset(queryset.order_by('-changed_on'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset.order_by('-changed_on'), many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        """Filter queryset based on user role and permissions"""
        user = self.request.user
        queryset = self.queryset
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by risk level if provided
        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(hse_risk_level=risk_level)
        
        # Filter by assigned user if provided
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter by mitigation department if provided
        mitigation_dept = self.request.query_params.get('mitigation_department')
        if mitigation_dept:
            queryset = queryset.filter(hse_mitigation_department_id=mitigation_dept)
        
        # Role-based filtering
        if hasattr(user, 'userprofile') and user.userprofile.role:
            role = user.userprofile.role.name.upper()
            if role == 'ADMIN':
                # Admin can see all HSE risk assessments
                pass
            elif role == 'MANAGER':
                # Manager can see assessments for their data groups
                user_data_groups = user.userprofile.data_groups.all()
                queryset = queryset.filter(
                    Q(business_unit__group__in=user_data_groups) |
                    Q(hse_mitigation_department__group__in=user_data_groups)
                )
            elif role == 'INSPECTOR':
                # Inspector can see assessments assigned to them
                queryset = queryset.filter(
                    Q(assigned_to=user) |
                    Q(hse_mitigation_assigned_to=user)
                )
            else:
                # Other users can only see assessments assigned to them
                queryset = queryset.filter(
                    Q(assigned_to=user) |
                    Q(hse_mitigation_assigned_to=user)
                )
        
        return queryset.order_by('-changed_on')
    
    def preprocess_data(self, data):
        """Convert names to IDs for related fields - same as regular evince viewset"""
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
    
    
    def create(self, request, *args, **kwargs):
        """Override create to return full detailed response - completely override parent logic"""
        try:
            data = request.data.copy()
            print(f"Original HSE data: {data}")
            
            data = self.preprocess_data(data)
            print(f"Preprocessed HSE data: {data}")

            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                print(f"HSE Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the instance using the serializer
            evince = serializer.save(changed_by=request.user)
            evince.save()
            
            # Debug: Check inspection analyses before creating tests and results
            print(f"HSE evince {evince.id} inspection_analyses count: {evince.inspection_analyses.count()}")
            for analysis in evince.inspection_analyses.all():
                print(f"  - Analysis: {analysis.name} (ID: {analysis.id})")
                params = analysis.parameter_set.all()
                print(f"    Parameters: {params.count()}")
                for param in params:
                    print(f"      - {param.name}")
            
            # Create inspection tests and results ONLY ONCE
            print(f"Creating inspection tests and results for HSE evince {evince.id}")
            self.create_inspection_tests_and_results(evince, is_update=False)
            
            # Return the full detailed response using the main serializer
            detailed_serializer = HSERiskAssessmentSerializer(evince, context={'request': request})
            headers = self.get_success_headers(detailed_serializer.data)
            return Response(detailed_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"Error in HSE create method: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        """Get dashboard statistics for HSE Risk Assessment"""
        queryset = self.get_queryset()
        
        stats = {
            'total_assessments': queryset.count(),
            'draft': queryset.filter(status='Logged').count(),
            'inspector_review': queryset.filter(status='InspectorReview').count(),
            'risk_validated': queryset.filter(status='RiskValidated').count(),
            'manager_assignment': queryset.filter(status='ManagerAssignment').count(),
            'lims_in_progress': queryset.filter(status='LIMSInProgress').count(),
            'lims_completed': queryset.filter(status='LIMSCompleted').count(),
            'manager_approval': queryset.filter(status='ManagerApproval').count(),
            'completed': queryset.filter(status='Approved').count(),
            'rejected': queryset.filter(status='Rejected').count(),
        }
        
        # Risk level distribution
        risk_levels = queryset.values('hse_risk_level').distinct()
        risk_distribution = {}
        for level in risk_levels:
            if level['hse_risk_level']:
                risk_distribution[level['hse_risk_level']] = queryset.filter(
                    hse_risk_level=level['hse_risk_level']
                ).count()
        
        stats['risk_distribution'] = risk_distribution
        
        return Response(stats)
    
    @action(detail=True, methods=['post'], url_path='assess-risk')
    def assess_risk(self, request, pk=None):
        """Inspector assesses the risk"""
        evince = self.get_object()
        
        # Validate that user is assigned inspector
        if evince.assigned_to != request.user:
            return Response(
                {'error': 'Only assigned inspector can assess risk'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate required fields
        required_fields = ['hse_risk_level', 'hse_risk_category', 'hse_observation_details']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update evince with risk assessment
        evince.hse_risk_level = request.data.get('hse_risk_level')
        evince.hse_risk_category = request.data.get('hse_risk_category')
        evince.hse_observation_details = request.data.get('hse_observation_details')
        evince.hse_risk_notes = request.data.get('hse_risk_notes', '')
        evince.hse_out_of_spec_results = request.data.get('hse_out_of_spec_results', [])
        evince.hse_inspection_date = timezone.now()
        evince.status = 'InspectorReview'
        evince.save()
        
        return Response({
            'message': 'Risk assessment completed successfully',
            'status': evince.status
        })
    
    @action(detail=True, methods=['post'], url_path='validate-risk')
    def validate_risk(self, request, pk=None):
        """Manager validates the risk assessment"""
        evince = self.get_object()
        
        # Check if user has manager permissions
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']:
            return Response(
                {'error': 'Only managers can validate risk assessments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        risk_valid = request.data.get('hse_risk_valid', False)
        rejection_reason = request.data.get('hse_risk_rejection_reason', '')
        
        if risk_valid:
            evince.hse_risk_valid = True
            evince.status = 'RiskValidated'
            evince.hse_risk_rejection_reason = None
        else:
            evince.hse_risk_valid = False
            evince.hse_risk_rejection_reason = rejection_reason
            evince.status = 'Rejected'
        
        evince.save()
        
        return Response({
            'message': f'Risk assessment {"validated" if risk_valid else "rejected"} successfully',
            'status': evince.status
        })
    
    @action(detail=True, methods=['post'], url_path='assign-mitigation')
    def assign_mitigation(self, request, pk=None):
        """Manager assigns mitigation work to department"""
        evince = self.get_object()
        
        # Check if user has manager permissions
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']:
            return Response(
                {'error': 'Only managers can assign mitigation work'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate required fields
        required_fields = ['hse_mitigation_department', 'hse_mitigation_assigned_to', 'hse_mitigation_target_date']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update evince with mitigation assignment
        evince.hse_mitigation_department_id = request.data.get('hse_mitigation_department')
        evince.hse_mitigation_assigned_to_id = request.data.get('hse_mitigation_assigned_to')
        evince.hse_mitigation_target_date = request.data.get('hse_mitigation_target_date')
        # Keep status as RiskValidated - don't change to ManagerAssignment
        # evince.status = 'ManagerAssignment'
        evince.save()
        
        return Response({
            'message': 'Mitigation work assigned successfully',
            'status': evince.status
        })
    
    @action(detail=True, methods=['post'], url_path='submit-mitigation-evidence')
    def submit_mitigation_evidence(self, request, pk=None):
        """Mitigation department submits evidence"""
        evince = self.get_object()
        
        # Validate that user is assigned for mitigation
        if evince.hse_mitigation_assigned_to != request.user:
            return Response(
                {'error': 'Only assigned mitigation user can submit evidence'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate required fields
        if 'hse_mitigation_actions' not in request.data:
            return Response(
                {'error': 'Missing required field: hse_mitigation_actions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update evince with mitigation evidence
        evince.hse_mitigation_actions = request.data.get('hse_mitigation_actions')
        evince.hse_mitigation_evidence = request.data.get('hse_mitigation_evidence', '')
        evince.hse_mitigation_completed = True
        evince.status = 'LIMSCompleted'
        evince.save()
        
        return Response({
            'message': 'Mitigation evidence submitted successfully',
            'status': evince.status
        })
    
    @action(detail=True, methods=['post'], url_path='approve-risk-closure')
    def approve_risk_closure(self, request, pk=None):
        """Manager approves risk closure"""
        evince = self.get_object()
        
        # Check if user has manager permissions
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role.name.upper() not in ['ADMIN', 'MANAGER']:
            return Response(
                {'error': 'Only managers can approve risk closure'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update evince with approval
        evince.hse_approved_by = request.user
        evince.hse_approved_at = timezone.now()
        evince.hse_risk_closed = True
        evince.status = 'Approved'
        evince.save()
        
        return Response({
            'message': 'Risk closure approved successfully',
            'status': evince.status
        })
    
    @action(detail=False, methods=['get'], url_path='workflow-states', permission_classes=[])
    def workflow_states(self, request):
        """Get available workflow states for HSE Risk Assessment"""
        states = [
            {'value': 'Logged', 'label': 'Draft - Admin logged inspection', 'color': 'gray'},
            {'value': 'InspectorReview', 'label': 'Inspector Review', 'color': 'blue'},
            {'value': 'RiskValidated', 'label': 'Risk Validated', 'color': 'green'},
            {'value': 'ManagerAssignment', 'label': 'Manager Assignment', 'color': 'orange'},
            {'value': 'MitigationInProgress', 'label': 'Mitigation In Progress', 'color': 'purple'},
            {'value': 'MitigationCompleted', 'label': 'Mitigation Completed', 'color': 'blue'},
            {'value': 'LIMSInProgress', 'label': 'LIMS In Progress', 'color': 'indigo'},
            {'value': 'LIMSCompleted', 'label': 'LIMS Completed', 'color': 'blue'},
            {'value': 'ManagerApproval', 'label': 'Manager Approval', 'color': 'yellow'},
            {'value': 'Approved', 'label': 'Approved', 'color': 'green'},
            {'value': 'Rejected', 'label': 'Rejected', 'color': 'red'},
        ]
        
        return Response(states)
    
    @action(detail=False, methods=['get'], url_path='risk-levels', permission_classes=[])
    def risk_levels(self, request):
        """Get available risk levels"""
        risk_levels = [
            {'value': 'LOW', 'label': 'Low'},
            {'value': 'MEDIUM', 'label': 'Medium'},
            {'value': 'HIGH', 'label': 'High'},
            {'value': 'CRITICAL', 'label': 'Critical'},
        ]
        return Response(risk_levels)
    
    @action(detail=False, methods=['get'], url_path='risk-categories', permission_classes=[])
    def risk_categories(self, request):
        """Get available risk categories"""
        categories = [
            {'value': 'Safety', 'label': 'Safety'},
            {'value': 'Health', 'label': 'Health'},
            {'value': 'Environmental', 'label': 'Environmental'},
            {'value': 'Equipment', 'label': 'Equipment'},
            {'value': 'Procedure', 'label': 'Procedure'},
        ]
        return Response(categories)
    
    @action(detail=True, methods=['post'], url_path='approve-mitigation')
    def approve_mitigation(self, request, pk=None):
        """Manager approves completed mitigation work"""
        try:
            evince = self.get_object()
            
            if evince.status != 'MitigationCompleted':
                return Response(
                    {'error': 'Only mitigation completed items can be approved'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update evince status
            evince.status = 'Approved'
            evince.hse_approved_by = request.user
            evince.hse_approved_at = timezone.now()
            evince.hse_manager_decision_final = True  # Mark as final decision
            evince.save()
            print(f"✅ Manager APPROVED evince {evince.id} - status set to 'Approved', manager_decision_final=True")
            
            return Response({
                'message': 'Mitigation work approved successfully',
                'status': evince.status,
                'approved_by': request.user.username,
                'approved_at': evince.hse_approved_at.isoformat()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to approve mitigation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='reject-mitigation')
    def reject_mitigation(self, request, pk=None):
        """Manager rejects completed mitigation work"""
        try:
            evince = self.get_object()
            rejection_reason = request.data.get('rejection_reason', '')
            
            if evince.status != 'MitigationCompleted':
                return Response(
                    {'error': 'Only mitigation completed items can be rejected'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not rejection_reason:
                return Response(
                    {'error': 'Rejection reason is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update evince status
            evince.status = 'Rejected'
            evince.hse_risk_rejection_reason = rejection_reason
            evince.hse_approved_by = request.user
            evince.hse_approved_at = timezone.now()
            evince.hse_manager_decision_final = True  # Mark as final decision
            evince.save()
            print(f"❌ Manager REJECTED evince {evince.id} - status set to 'Rejected', manager_decision_final=True")
            
            return Response({
                'message': 'Mitigation work rejected successfully',
                'status': evince.status,
                'rejection_reason': rejection_reason,
                'rejected_by': request.user.username,
                'rejected_at': evince.hse_approved_at.isoformat()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to reject mitigation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='reassign-mitigation')
    def reassign_mitigation(self, request, pk=None):
        """Manager reassigns mitigation to different department"""
        try:
            evince = self.get_object()
            new_department_id = request.data.get('new_department_id')
            reassignment_reason = request.data.get('reassignment_reason', '')
            
            # Debug logging
            print(f"🔍 Reassignment Debug - Evince ID: {evince.id}")
            print(f"🔍 Reassignment Debug - Evince Status: {evince.status}")
            print(f"🔍 Reassignment Debug - Evince Type: {evince.evince_type}")
            print(f"🔍 Reassignment Debug - Request Data: {request.data}")
            print(f"🔍 Reassignment Debug - New Department ID: {new_department_id} (type: {type(new_department_id)})")
            print(f"🔍 Reassignment Debug - Reassignment Reason: {reassignment_reason}")
            
            # Check if evince has any existing assignments
            from inspection_management.models import ExternalDepartmentAssignment
            existing_assignments = ExternalDepartmentAssignment.objects.filter(evince=evince)
            print(f"🔍 Existing assignments count: {existing_assignments.count()}")
            for assignment in existing_assignments:
                print(f"  - Assignment ID: {assignment.id}, Status: {assignment.status}, Department: {assignment.external_department.name}")
            
            # Check available departments
            from inspection_management.models import ExternalDepartment
            all_departments = ExternalDepartment.objects.all()
            print(f"🔍 Available departments count: {all_departments.count()}")
            for dept in all_departments:
                print(f"  - Department ID: {dept.id}, Name: {dept.name}, External System ID: {dept.external_system_id}")
            
            if evince.status != 'MitigationCompleted':
                print(f"❌ Status validation failed: {evince.status} != MitigationCompleted")
                return Response(
                    {'error': f'Only mitigation completed items can be reassigned. Current status: {evince.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not new_department_id:
                print(f"❌ Department ID validation failed: {new_department_id}")
                return Response(
                    {'error': 'New department ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the new department
            from inspection_management.models import ExternalDepartment
            try:
                # Convert to integer if it's a string
                if isinstance(new_department_id, str):
                    new_department_id = int(new_department_id)
                
                print(f"🔍 Looking for department with ID: {new_department_id}")
                new_department = ExternalDepartment.objects.get(id=new_department_id)
                print(f"✅ Found department: {new_department.name}")
            except ExternalDepartment.DoesNotExist:
                print(f"❌ Department not found with ID: {new_department_id}")
                return Response(
                    {'error': f'New department not found with ID: {new_department_id}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except ValueError as e:
                print(f"❌ Invalid department ID format: {new_department_id}")
                return Response(
                    {'error': f'Invalid department ID format: {new_department_id}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update evince status and department
            evince.status = 'MitigationInProgress'
            evince.assigned_department = new_department.name
            evince.hse_risk_rejection_reason = f"Reassigned to {new_department.name}. Reason: {reassignment_reason}"
            evince.save()
            
            # Update existing assignment record instead of creating new one
            from inspection_management.models import ExternalDepartmentAssignment
            
            # Find the existing assignment for this evince
            existing_assignment = ExternalDepartmentAssignment.objects.filter(
                evince=evince
            ).first()
            
            # Initialize external_success variable
            external_success = False
            
            if existing_assignment:
                # Update existing assignment
                existing_assignment.external_department = new_department
                existing_assignment.assigned_by = request.user
                
                # Handle target date properly - convert ISO string to datetime if provided
                target_date = request.data.get('new_target_date')
                if target_date:
                    try:
                        from django.utils.dateparse import parse_datetime
                        from django.utils import timezone
                        
                        parsed_date = parse_datetime(target_date)
                        if parsed_date:
                            # Convert to local timezone if it's UTC
                            if parsed_date.tzinfo is None:
                                # If no timezone info, assume it's UTC
                                parsed_date = timezone.make_aware(parsed_date, timezone.utc)
                            
                            # Convert to local timezone for storage
                            local_date = timezone.localtime(parsed_date)
                            existing_assignment.target_completion_date = local_date
                            print(f"✅ Updated target_completion_date: {local_date} (original: {target_date})")
                        else:
                            print(f"⚠️ Could not parse target date: {target_date}")
                    except Exception as e:
                        print(f"❌ Error parsing target date {target_date}: {str(e)}")
                else:
                    print(f"⚠️ No target date provided in reassignment")
                
                existing_assignment.notes = f"Reassigned from previous department. Reason: {reassignment_reason}"
                existing_assignment.priority = request.data.get('priority', 'MEDIUM')
                existing_assignment.assigned_user = request.data.get('assigned_user', '')
                existing_assignment.status = 'ASSIGNED'
                existing_assignment.save()
                
                print(f"✅ Updated existing assignment {existing_assignment.id} for evince {evince.id}")
                
                # Send updated assignment to external system
                from api.viewsets.external_departments import ExternalDepartmentViewSet
                external_viewset = ExternalDepartmentViewSet()
                external_success = external_viewset.send_assignment_to_external_system(existing_assignment, new_department, is_update=True)
                
                if external_success:
                    print(f"✅ Reassignment sent to external system successfully for evince {evince.id}")
                else:
                    print(f"❌ Failed to send reassignment to external system for evince {evince.id}")
                    
            else:
                # Fallback: Create new assignment if none exists (shouldn't happen)
                print(f"⚠️ No existing assignment found for evince {evince.id}, creating new one")
                
                # Generate sequential external task ID for new assignment
                existing_assignments = ExternalDepartmentAssignment.objects.filter(
                    external_task_id__startswith='Mitigation-EID-'
                ).values_list('external_task_id', flat=True)
                
                max_id = 0
                for task_id in existing_assignments:
                    try:
                        if task_id and task_id.startswith('Mitigation-EID-'):
                            number_str = task_id.replace('Mitigation-EID-', '')
                            number = int(number_str)
                            if number > max_id:
                                max_id = number
                    except (ValueError, AttributeError):
                        continue
                
                external_task_id = f'Mitigation-EID-{max_id + 1}'
                
                # Handle target date properly for new assignment
                target_date = request.data.get('new_target_date')
                parsed_target_date = None
                if target_date:
                    try:
                        from django.utils.dateparse import parse_datetime
                        from django.utils import timezone
                        
                        parsed_date = parse_datetime(target_date)
                        if parsed_date:
                            # Convert to local timezone if it's UTC
                            if parsed_date.tzinfo is None:
                                # If no timezone info, assume it's UTC
                                parsed_date = timezone.make_aware(parsed_date, timezone.utc)
                            
                            # Convert to local timezone for storage
                            parsed_target_date = timezone.localtime(parsed_date)
                            print(f"✅ Parsed target_completion_date for new assignment: {parsed_target_date} (original: {target_date})")
                    except Exception as e:
                        print(f"❌ Error parsing target date for new assignment {target_date}: {str(e)}")

                new_assignment = ExternalDepartmentAssignment.objects.create(
                    evince=evince,
                    external_department=new_department,
                    assigned_by=request.user,
                    target_completion_date=parsed_target_date,
                    notes=f"Reassigned from previous department. Reason: {reassignment_reason}",
                    priority=request.data.get('priority', 'MEDIUM'),
                    assigned_user=request.data.get('assigned_user', ''),
                    external_task_id=external_task_id,
                    status='ASSIGNED'
                )
                
                # Send new assignment to external system
                from api.viewsets.external_departments import ExternalDepartmentViewSet
                external_viewset = ExternalDepartmentViewSet()
                external_success = external_viewset.send_assignment_to_external_system(new_assignment, new_department)
                
                if external_success:
                    print(f"✅ New assignment sent to external system successfully for evince {evince.id}")
                else:
                    print(f"❌ Failed to send new assignment to external system for evince {evince.id}")
            
            # Prepare response data
            response_data = {
                'message': f'Mitigation reassigned to {new_department.name} successfully',
                'status': evince.status,
                'new_department': new_department.name,
                'reassignment_reason': reassignment_reason,
                'reassigned_by': request.user.username,
                'reassigned_at': timezone.now().isoformat(),
                'external_system_sent': external_success,
                'external_system_message': 'Reassignment sent to external system' if external_success else 'Failed to send to external system'
            }
            
            # Add external_task_id only if it exists
            if existing_assignment:
                response_data['external_task_id'] = existing_assignment.external_task_id
            elif 'external_task_id' in locals():
                response_data['external_task_id'] = external_task_id
            
            return Response(response_data)
            
        except Exception as e:
            print(f"❌ Unexpected error in reassign_mitigation: {str(e)}")
            print(f"❌ Error type: {type(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to reassign mitigation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
