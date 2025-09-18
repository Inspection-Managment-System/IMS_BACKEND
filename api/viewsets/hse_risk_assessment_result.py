from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator

from api.serializers.hse_risk_assessment_result import (
    HSERiskAssessmentResultSerializer,
    HSERiskAssessmentResultCreateSerializer,
    HSERiskAssessmentResultUpdateSerializer
)
from inspection_management.models import HSERiskAssessmentResult, Evince
from users.authorization import role_required
from api.services.hse_risk_workflow_service import HSERiskWorkflowService


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class HSERiskAssessmentResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HSE Risk Assessment Results
    """
    queryset = HSERiskAssessmentResult.objects.all().order_by('-created_on')
    serializer_class = HSERiskAssessmentResultSerializer
    permission_classes = []

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action
        """
        if self.action == 'create':
            return HSERiskAssessmentResultCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return HSERiskAssessmentResultUpdateSerializer
        return HSERiskAssessmentResultSerializer

    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()
        
        # Filter by evince ID
        evince_id = self.request.query_params.get('evince', None)
        if evince_id:
            queryset = queryset.filter(evince_id=evince_id)
        
        # Filter by parameter status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(parameter_status=status)
        
        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level', None)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new HSE Risk Assessment Result
        """
        print(f"=== DEBUG: Creating HSE Risk Assessment Result ===")
        print(f"Request data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if evince exists and is HSE Risk Management type
        evince_id = request.data.get('evince')
        if evince_id:
            evince = get_object_or_404(Evince, id=evince_id)
            if evince.evince_type != 'hse_risk_management':
                return Response(
                    {"error": "Evince must be of type 'hse_risk_management'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        instance = serializer.save()
        print(f"Created HSE Risk Assessment Result: {instance.id}")
        
        return Response(
            HSERiskAssessmentResultSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """
        Update an existing HSE Risk Assessment Result
        """
        print(f"=== DEBUG: Updating HSE Risk Assessment Result {kwargs.get('pk')} ===")
        print(f"Request data: {request.data}")
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        instance = serializer.save()
        print(f"Updated HSE Risk Assessment Result: {instance.id}")
        
        return Response(HSERiskAssessmentResultSerializer(instance).data)

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        Create multiple HSE Risk Assessment Results for an evince
        """
        print(f"=== DEBUG: Bulk creating HSE Risk Assessment Results ===")
        print(f"Request data: {request.data}")
        
        evince_id = request.data.get('evince_id')
        parameters = request.data.get('parameters', [])
        
        if not evince_id or not parameters:
            return Response(
                {"error": "evince_id and parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if evince exists and is HSE Risk Management type
        evince = get_object_or_404(Evince, id=evince_id)
        if evince.evince_type != 'hse_risk_management':
            return Response(
                {"error": "Evince must be of type 'hse_risk_management'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_results = []
        for param_data in parameters:
            param_data['evince'] = evince_id
            serializer = HSERiskAssessmentResultCreateSerializer(data=param_data)
            if serializer.is_valid():
                instance = serializer.save(changed_by=request.user)
                created_results.append(HSERiskAssessmentResultSerializer(instance).data)
            else:
                print(f"Validation error for parameter {param_data}: {serializer.errors}")
                return Response(
                    {"error": f"Validation error for parameter: {serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        print(f"Bulk created {len(created_results)} HSE Risk Assessment Results")
        return Response(created_results, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='by-evinces')
    def get_by_evinces(self, request):
        """
        Get HSE Risk Assessment Results grouped by evince
        """
        evince_ids = request.query_params.getlist('evince_ids')
        if not evince_ids:
            return Response(
                {"error": "evince_ids parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = self.get_queryset().filter(evince_id__in=evince_ids)
        
        # Group by evince
        grouped_results = {}
        for result in results:
            evince_id = result.evince_id
            if evince_id not in grouped_results:
                grouped_results[evince_id] = []
            grouped_results[evince_id].append(HSERiskAssessmentResultSerializer(result).data)
        
        return Response(grouped_results)

    @action(detail=True, methods=['post'], url_path='update-parameter')
    def update_parameter(self, request, pk=None):
        """
        Update a specific parameter value
        """
        print(f"=== DEBUG: Updating parameter for HSE Risk Assessment Result {pk} ===")
        print(f"Request data: {request.data}")
        
        instance = get_object_or_404(HSERiskAssessmentResult, pk=pk)
        
        parameter_value = request.data.get('parameter_value')
        parameter_comments = request.data.get('parameter_comments', '')
        
        if parameter_value is None:
            return Response(
                {"error": "parameter_value is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.parameter_value = parameter_value
        instance.parameter_comments = parameter_comments
        instance.parameter_status = 'Completed'
        instance.changed_by = request.user
        instance.save()
        
        print(f"Updated parameter for HSE Risk Assessment Result: {instance.id}")
        
        return Response(
            {"message": "Parameter updated successfully"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='update-risk-assessment')
    def update_risk_assessment(self, request, pk=None):
        """
        Update risk assessment details
        """
        print(f"=== DEBUG: Updating risk assessment for HSE Risk Assessment Result {pk} ===")
        print(f"Request data: {request.data}")
        
        instance = get_object_or_404(HSERiskAssessmentResult, pk=pk)
        
        # Update risk assessment fields
        risk_fields = [
            'risk_level', 'risk_category', 'risk_notes', 
            'observation_details', 'risk_valid'
        ]
        
        for field in risk_fields:
            if field in request.data:
                setattr(instance, field, request.data[field])
        
        instance.changed_by = request.user
        instance.save()
        
        print(f"Updated risk assessment for HSE Risk Assessment Result: {instance.id}")
        
        return Response(
            {"message": "Risk assessment updated successfully"},
            status=status.HTTP_200_OK
        )

    # Manager Workflow Endpoints
    @action(detail=False, methods=['get'], url_path='manager-queue')
    def manager_queue(self, request):
        """
        Get HSE risk assessments assigned to manager for review with pagination
        """
        manager_id = request.user.id
        
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        # Get paginated risk assessments
        paginated_data = HSERiskWorkflowService.get_manager_risk_assessments(manager_id, page, page_size)
        risk_assessments = paginated_data['results']
        
        # Serialize the evinces with their risk assessment results
        result_data = []
        for evince in risk_assessments:
            evince_data = {
                'id': evince.id,
                'name': evince.name,
                'description': evince.description,
                'status': evince.status,
                'business_unit': evince.business_unit.name if evince.business_unit else None,
                'inspection_point': evince.inspection_point.name if evince.inspection_point else None,
                'hse_risk_level': evince.hse_risk_level,
                'hse_risk_category': evince.hse_risk_category,
                'hse_risk_valid': evince.hse_risk_valid,
                'hse_out_of_spec_results': evince.hse_out_of_spec_results,
                'hse_observation_details': evince.hse_observation_details,
                'hse_mitigation_actions': evince.hse_mitigation_actions,
                'hse_mitigation_completed': evince.hse_mitigation_completed,
                'hse_risk_closed': evince.hse_risk_closed,
                'start_date_time': evince.start_date_time,
                'end_date_time': evince.end_date_time,
                'hse_follow_up_date': evince.hse_follow_up_date,
                'hse_mitigation_target_date': evince.hse_mitigation_target_date,
                'changed_on': evince.changed_on,
                'assigned_to': evince.assigned_to.username if evince.assigned_to else None,
                'reviewed_by': evince.reviewed_by.username if evince.reviewed_by else None,
                'risk_assessment_results': []
            }
            
            # Get risk assessment results for this evince
            risk_results = HSERiskAssessmentResult.objects.filter(evince=evince)
            for result in risk_results:
                evince_data['risk_assessment_results'].append({
                    'id': result.id,
                    'parameter_name': result.parameter_name,
                    'parameter_value': result.parameter_value,
                    'parameter_comments': result.parameter_comments,
                    'parameter_status': result.parameter_status,
                    'risk_level': result.risk_level,
                    'risk_category': result.risk_category,
                    'risk_notes': result.risk_notes,
                    'observation_details': result.observation_details,
                    'risk_valid': result.risk_valid
                })
            
            result_data.append(evince_data)
        
        # Return paginated response
        return Response({
            'results': result_data,
            'total_count': paginated_data['total_count'],
            'page': paginated_data['page'],
            'page_size': paginated_data['page_size'],
            'total_pages': paginated_data['total_pages'],
            'has_next': paginated_data['has_next'],
            'has_previous': paginated_data['has_previous']
        })

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_risk_assessment(self, request, pk=None):
        """
        Manager approves HSE risk assessment
        """
        evince_id = pk
        manager_id = request.user.id
        approval_notes = request.data.get('approval_notes', '')
        
        evince = HSERiskWorkflowService.approve_risk_assessment(evince_id, manager_id, approval_notes)
        
        if evince:
            return Response({
                'message': 'Risk assessment approved successfully',
                'evince_id': evince.id,
                'status': evince.status
            })
        else:
            return Response(
                {'error': 'Failed to approve risk assessment'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_risk_assessment(self, request, pk=None):
        """
        Manager rejects HSE risk assessment
        """
        evince_id = pk
        manager_id = request.user.id
        rejection_reason = request.data.get('rejection_reason', '')
        
        if not rejection_reason:
            return Response(
                {'error': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evince = HSERiskWorkflowService.reject_risk_assessment(evince_id, manager_id, rejection_reason)
        
        if evince:
            return Response({
                'message': 'Risk assessment rejected successfully',
                'evince_id': evince.id,
                'status': evince.status
            })
        else:
            return Response(
                {'error': 'Failed to reject risk assessment'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='assign-mitigation')
    def assign_mitigation(self, request, pk=None):
        """
        Manager assigns mitigation to external department
        """
        evince_id = pk
        external_dept_id = request.data.get('external_department_id')
        manager_id = request.user.id
        mitigation_plan = request.data.get('mitigation_plan', '')
        target_date = request.data.get('target_date')
        
        if not external_dept_id:
            return Response(
                {'error': 'External department ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not mitigation_plan:
            return Response(
                {'error': 'Mitigation plan is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evince, assignment = HSERiskWorkflowService.assign_mitigation_to_external_department(
            evince_id, external_dept_id, manager_id, mitigation_plan, target_date
        )
        
        if evince and assignment:
            return Response({
                'message': 'Mitigation assigned successfully',
                'evince_id': evince.id,
                'assignment_id': assignment.id,
                'status': evince.status
            })
        else:
            return Response(
                {'error': 'Failed to assign mitigation'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='external-departments')
    def get_external_departments(self, request):
        """
        Get available external departments for assignment
        """
        departments = HSERiskWorkflowService.get_available_external_departments()
        
        result_data = []
        for dept in departments:
            result_data.append({
                'id': dept.id,
                'name': dept.name,
                'department_type': dept.department_type,
                'description': dept.description,
                'contact_person': dept.contact_person,
                'contact_email': dept.contact_email,
                'contact_phone': dept.contact_phone,
                'capabilities': dept.capabilities,
                'specializations': dept.specializations,
                'is_available_for_assignment': dept.is_available_for_assignment
            })
        
        return Response(result_data)

    @action(detail=True, methods=['post'], url_path='complete-mitigation')
    def complete_mitigation(self, request, pk=None):
        """
        External department completes mitigation work
        """
        evince_id = pk
        completion_notes = request.data.get('completion_notes', '')
        evidence_data = request.data.get('evidence_data', {})
        
        if not completion_notes:
            return Response(
                {'error': 'Completion notes are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evince = HSERiskWorkflowService.complete_mitigation(evince_id, completion_notes, evidence_data)
        
        if evince:
            return Response({
                'message': 'Mitigation completed successfully',
                'evince_id': evince.id,
                'status': evince.status
            })
        else:
            return Response(
                {'error': 'Failed to complete mitigation'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='verify-mitigation')
    def verify_mitigation(self, request, pk=None):
        """
        Manager verifies mitigation completion
        """
        evince_id = pk
        manager_id = request.user.id
        verification_notes = request.data.get('verification_notes', '')
        
        evince = HSERiskWorkflowService.verify_mitigation_completion(evince_id, manager_id, verification_notes)
        
        if evince:
            return Response({
                'message': 'Mitigation verified successfully',
                'evince_id': evince.id,
                'status': evince.status
            })
        else:
            return Response(
                {'error': 'Failed to verify mitigation'},
                status=status.HTTP_400_BAD_REQUEST
            )
