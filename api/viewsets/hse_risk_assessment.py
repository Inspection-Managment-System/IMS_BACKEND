from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from inspection_management.models import Evince
from api.serializers.hse_risk_assessment import (
    HSERiskAssessmentSerializer,
    HSERiskAssessmentCreateSerializer,
    HSERiskAssessmentUpdateSerializer
)


class HSERiskAssessmentViewSet(viewsets.ModelViewSet):
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
    
    def perform_create(self, serializer):
        """Set created_by to current user and create inspection tests"""
        evince = serializer.save(changed_by=self.request.user)
        # Create inspection tests and results for the evince (async or on-demand)
        # Only create if inspection_analyses are provided and create_tests is True
        create_tests = self.request.data.get('create_tests', True)
        if create_tests and evince.inspection_analyses.exists():
            self.create_inspection_tests_and_results(evince)
    
    def create(self, request, *args, **kwargs):
        """Override create to return full detailed response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return the full detailed response using the main serializer
        detailed_serializer = HSERiskAssessmentSerializer(serializer.instance, context={'request': request})
        headers = self.get_success_headers(detailed_serializer.data)
        return Response(detailed_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def create_inspection_tests_and_results(self, evince):
        """Create inspection tests and results for the evince - optimized version"""
        from inspection_management.models import InspectionTest, InspectionResult, Parameter
        
        # Bulk create inspection tests
        inspection_tests = []
        for inspection_analysis in evince.inspection_analyses.all():
            inspection_tests.append(InspectionTest(
                evince=evince,
                inspection_analysis=inspection_analysis,
                changed_by=evince.changed_by,
            ))
        
        if inspection_tests:
            InspectionTest.objects.bulk_create(inspection_tests)
            
            # Get all parameters for all inspection analyses at once
            analysis_ids = [test.inspection_analysis.id for test in inspection_tests]
            parameters = Parameter.objects.filter(inspection_analysis_id__in=analysis_ids)
            
            # Create parameter lookup for efficient mapping
            param_lookup = {}
            for param in parameters:
                if param.inspection_analysis.id not in param_lookup:
                    param_lookup[param.inspection_analysis.id] = []
                param_lookup[param.inspection_analysis.id].append(param)
            
            # Bulk create inspection results
            inspection_results = []
            for test in inspection_tests:
                test_params = param_lookup.get(test.inspection_analysis.id, [])
                for parameter in test_params:
                    inspection_results.append(InspectionResult(
                        evince=evince,
                        inspection_test=test,
                        changed_by=evince.changed_by,
                    ))
            
            if inspection_results:
                InspectionResult.objects.bulk_create(inspection_results)
    
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
        evince.status = 'ManagerAssignment'
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
            {'value': 'LIMSInProgress', 'label': 'LIMS In Progress', 'color': 'purple'},
            {'value': 'LIMSCompleted', 'label': 'LIMS Completed', 'color': 'indigo'},
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
