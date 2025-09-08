from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from inspection_management.models.hse_workflow_models import HSEObservation, HSEWorkflowHistory, HSEEvidence
from api.serializers.hse_serializers import HSEObservationSerializer, HSEWorkflowHistorySerializer, HSEEvidenceSerializer
from api.services.hse_workflow_service import HSEWorkflowService
from django.db import models


class HSEObservationViewSet(viewsets.ModelViewSet):
    """HSE Observation API with workflow actions"""
    queryset = HSEObservation.objects.all()
    serializer_class = HSEObservationSerializer
    permission_classes = []  # Temporarily remove authentication requirement
    
    def perform_create(self, serializer):
        """Set created_by to current user and use workflow service"""
        try:
            # Use the workflow service to create observation with proper workflow initialization
            from api.services.hse_workflow_service import HSEWorkflowService
            observation = HSEWorkflowService.create_observation_with_workflow(
                serializer.validated_data, 
                self.request.user
            )
            return observation
        except Exception as e:
            print(f"Error in perform_create: {e}")
            raise
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        
        # Handle anonymous users (no authentication)
        if user.is_anonymous:
            return HSEObservation.objects.all()
        
        # If user has no role field or role is not set, treat as admin
        if not hasattr(user, 'role') or not user.role:
            # For users without roles, show all observations they created or are assigned to
            return HSEObservation.objects.filter(
                models.Q(created_by=user) | models.Q(assigned_to=user)
            ).distinct()
        
        # Admin can see all observations
        if user.role == 'ADMIN':
            return HSEObservation.objects.all()
        
        # Manager can see observations for their departments
        elif user.role == 'MANAGER':
            # Assuming user has departments field, adjust based on your user model
            return HSEObservation.objects.filter(affected_department__in=getattr(user, 'departments', []))
        
        # Regular users can only see observations assigned to them
        else:
            return HSEObservation.objects.filter(assigned_to=user)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        try:
            user = request.user
            queryset = self.get_queryset()

            stats = {
                'total_observations': queryset.count(),
                'pending': queryset.filter(workflow_state='PENDING_VALIDATION').count(),
                'in_progress': queryset.filter(workflow_state='IN_PROGRESS').count(),
                'completed': queryset.filter(workflow_state='CLOSED').count(),
                'assigned': queryset.filter(workflow_state='ASSIGNED').count(),
                'draft': queryset.filter(workflow_state='DRAFT').count(),
                'evidence_submitted': queryset.filter(workflow_state='EVIDENCE_SUBMITTED').count(),
            }

            return Response(stats)
        except Exception as e:
            # Return default stats if there's an error
            return Response({
                'total_observations': 0,
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'assigned': 0,
                'draft': 0,
                'evidence_submitted': 0,
            })
    
    @action(detail=False, methods=['get'])
    def risk_levels(self, request):
        """Get available risk levels"""
        risk_levels = [
            {'value': 'LOW', 'label': 'Low'},
            {'value': 'MEDIUM', 'label': 'Medium'},
            {'value': 'HIGH', 'label': 'High'},
            {'value': 'CRITICAL', 'label': 'Critical'},
        ]
        return Response(risk_levels)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get available categories"""
        categories = [
            {'value': 'SAFETY', 'label': 'Safety'},
            {'value': 'HEALTH', 'label': 'Health'},
            {'value': 'ENVIRONMENTAL', 'label': 'Environmental'},
            {'value': 'EQUIPMENT', 'label': 'Equipment'},
            {'value': 'PROCEDURE', 'label': 'Procedure'},
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def available_users(self, request):
        """Get available users for assignment"""
        try:
            from users.models.user import User
            users = User.objects.filter(is_active=True).values('id', 'username', 'first_name', 'last_name', 'role')
            return Response(users)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def workflow_states(self, request):
        """Get available workflow states and transitions"""
        workflow_states = [
            {'value': 'DRAFT', 'label': 'Draft', 'color': 'gray'},
            {'value': 'PENDING_VALIDATION', 'label': 'Pending Validation', 'color': 'yellow'},
            {'value': 'ASSIGNED', 'label': 'Assigned', 'color': 'blue'},
            {'value': 'IN_PROGRESS', 'label': 'In Progress', 'color': 'orange'},
            {'value': 'EVIDENCE_SUBMITTED', 'label': 'Evidence Submitted', 'color': 'purple'},
            {'value': 'CLOSED', 'label': 'Closed', 'color': 'green'},
        ]
        
        valid_transitions = {
            'DRAFT': ['PENDING_VALIDATION'],
            'PENDING_VALIDATION': ['ASSIGNED', 'DRAFT'],
            'ASSIGNED': ['IN_PROGRESS'],
            'IN_PROGRESS': ['EVIDENCE_SUBMITTED', 'ASSIGNED'],
            'EVIDENCE_SUBMITTED': ['CLOSED', 'IN_PROGRESS'],
            'CLOSED': []
        }
        
        return Response({
            'states': workflow_states,
            'transitions': valid_transitions
        })
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update observation workflow state"""
        observation = self.get_object()
        new_state = request.data.get('workflow_state')

        if not new_state:
            return Response(
                {'error': 'workflow_state is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use workflow service to validate and perform transition
        from api.services.hse_workflow_service import HSEWorkflowService
        
        if not HSEWorkflowService.can_transition_status(observation, new_state):
            return Response(
                {'error': f'Cannot transition from {observation.workflow_state} to {new_state}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Perform the transition using workflow service
        try:
            HSEWorkflowService.transition_state(observation, new_state, request.user)
            return Response({
                'status': 'updated',
                'old_state': observation.workflow_state,
                'new_state': new_state
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to update status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """Assign observation to a user"""
        observation = self.get_object()
        assignee_id = request.data.get('assignee')
        
        if not assignee_id:
            return Response(
                {'error': 'assignee is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from users.models.user import User
        try:
            assignee = User.objects.get(id=assignee_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        observation.assigned_to = assignee
        observation.save()
        
        # Create workflow history entry
        HSEWorkflowHistory.objects.create(
            observation=observation,
            action=f'Assigned to {assignee.username}',
            performed_by=request.user,
            status=observation.status
        )
        
        return Response({'status': 'assigned'})
    
    @action(detail=True, methods=['post'])
    def validate_risk(self, request, pk=None):
        """Validate HSE observation risk"""
        observation = self.get_object()
        user = request.user
        
        if not HSEWorkflowService.can_validate(user, observation):
            return Response(
                {'error': 'Cannot validate this observation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        HSEWorkflowService.transition_state(observation, 'PENDING_VALIDATION', user)
        observation.validated_by = user
        observation.save()
        
        return Response({'status': 'validated'})
    
    @action(detail=True, methods=['post'])
    def assign_user(self, request, pk=None):
        """Assign observation to a user"""
        observation = self.get_object()
        user = request.user
        assigned_user_id = request.data.get('assigned_user_id')
        target_date = request.data.get('target_date')
        
        if not HSEWorkflowService.can_assign(user, observation):
            return Response(
                {'error': 'Cannot assign this observation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not assigned_user_id:
            return Response(
                {'error': 'assigned_user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from users.models.user import User
        try:
            assigned_user = User.objects.get(id=assigned_user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        observation.assigned_to = assigned_user
        observation.target_date = target_date
        HSEWorkflowService.transition_state(observation, 'ASSIGNED', user)
        
        return Response({'status': 'assigned'})
    
    @action(detail=True, methods=['post'])
    def submit_evidence(self, request, pk=None):
        """Submit evidence for observation"""
        observation = self.get_object()
        user = request.user
        
        if not HSEWorkflowService.can_submit_evidence(user, observation):
            return Response(
                {'error': 'Cannot submit evidence'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        HSEWorkflowService.transition_state(observation, 'EVIDENCE_SUBMITTED', user)
        
        return Response({'status': 'evidence_submitted'})
    
    @action(detail=True, methods=['post'])
    def close_observation(self, request, pk=None):
        """Close HSE observation"""
        observation = self.get_object()
        user = request.user
        
        if not HSEWorkflowService.can_close(user, observation):
            return Response(
                {'error': 'Cannot close this observation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        HSEWorkflowService.transition_state(observation, 'CLOSED', user)
        
        return Response({'status': 'closed'})


class HSEWorkflowHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """HSE Workflow History API"""
    queryset = HSEWorkflowHistory.objects.all()
    serializer_class = HSEWorkflowHistorySerializer
    permission_classes = []  # Temporarily remove authentication requirement
    
    def get_queryset(self):
        """Filter by observation_id if provided"""
        observation_id = self.request.query_params.get('observation_id')
        if observation_id:
            return HSEWorkflowHistory.objects.filter(observation_id=observation_id)
        return HSEWorkflowHistory.objects.all()  # Return all history entries instead of none


class HSEEvidenceViewSet(viewsets.ModelViewSet):
    """HSE Evidence API"""
    queryset = HSEEvidence.objects.all()
    serializer_class = HSEEvidenceSerializer
    permission_classes = []  # Temporarily remove authentication requirement
    
    def perform_create(self, serializer):
        """Set uploaded_by to current user"""
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        """Filter by observation_id if provided"""
        observation_id = self.request.query_params.get('observation_id')
        if observation_id:
            return HSEEvidence.objects.filter(observation_id=observation_id)
        return HSEEvidence.objects.all()
