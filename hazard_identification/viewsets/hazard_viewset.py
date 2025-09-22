from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from hazard_identification.models import HazardIdentification, HazardEvidence
from hazard_identification.serializers import (
    HazardIdentificationSerializer,
    HazardIdentificationListSerializer,
    HazardIdentificationCreateSerializer,
    HazardEvidenceSerializer,
    HazardAssignmentSerializer,
    HazardStatusUpdateSerializer
)
from inspection_management.models import BusinessUnit
from users.models.user import User


class HazardIdentificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing hazard identification log entries"""
    
    queryset = HazardIdentification.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['hazard_description', 'location', 'serial_number']
    ordering_fields = ['reported_date', 'target_completion_date', 'severity_level', 'priority_level']
    ordering = ['-reported_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return HazardIdentificationListSerializer
        elif self.action == 'create':
            return HazardIdentificationCreateSerializer
        elif self.action in ['assign', 'update_status']:
            return HazardIdentificationSerializer
        else:
            return HazardIdentificationSerializer
    
    def get_queryset(self):
        """Filter hazards based on user role and permissions"""
        queryset = HazardIdentification.objects.select_related(
            'reported_by', 'assigned_to', 'assigned_department', 
            'business_unit', 'category', 'reviewed_by'
        ).prefetch_related('evidence')
        
        user = self.request.user
        
        # Get user role from userprofile
        user_role = None
        if hasattr(user, 'userprofile') and user.userprofile and user.userprofile.role:
            user_role = user.userprofile.role.name
        
        # Filter based on user role (case-insensitive)
        if user_role and user_role.upper() in ['ADMIN']:
            # Admin can see all hazards
            pass
        elif user_role and user_role.upper() in ['MANAGER']:
            # Manager can see hazards in their business units
            manager_data_groups = user.userprofile.data_groups.all()
            data_group_ids = manager_data_groups.values_list('id', flat=True)
            business_units = BusinessUnit.objects.filter(group_id__in=data_group_ids)
            business_unit_ids = business_units.values_list('id', flat=True)
            queryset = queryset.filter(business_unit_id__in=business_unit_ids)
        elif user_role and user_role.upper() in ['INSPECTOR']:
            # Inspector can see hazards they reported or are assigned to
            queryset = queryset.filter(
                Q(reported_by=user) | Q(assigned_to=user)
            )
        else:
            # Other users can only see hazards they reported
            queryset = queryset.filter(reported_by=user)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by overdue hazards
        overdue = self.request.query_params.get('overdue', None)
        if overdue == 'true':
            queryset = queryset.filter(
                target_completion_date__lt=timezone.now(),
                status__in=['Logged', 'InspectorReview', 'ManagerAssignment', 'InProgress']
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the reported_by user when creating a hazard"""
        serializer.save(reported_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def upload_evidence(self, request, pk=None):
        """Upload evidence photos for a hazard"""
        try:
            print(f"🔍 Attempting to upload evidence for hazard ID: {pk}")
            print(f"🔍 Request user: {request.user}")
            print(f"🔍 Request method: {request.method}")
            
            # Check if hazard exists first
            try:
                hazard = HazardIdentification.objects.get(pk=pk)
                print(f"✅ Found hazard: {hazard.id} - {hazard.hazard_description[:50]}")
            except HazardIdentification.DoesNotExist:
                print(f"❌ Hazard with ID {pk} does not exist")
                return Response(
                    {'error': f'Hazard with ID {pk} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Now use get_object() for permission checking
            hazard = self.get_object()
            
            # Get uploaded files
            files = request.FILES.getlist('images')
            evidence_type = request.data.get('evidence_type', 'before')
            description = request.data.get('description', '')
            
            print(f"Files received: {len(files)}")
            print(f"Evidence type: {evidence_type}")
            print(f"Description: {description}")
            print(f"User: {request.user}")
            
            if not files:
                return Response(
                    {'error': 'No images provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if evidence_type not in ['before', 'after']:
                return Response(
                    {'error': 'Evidence type must be "before" or "after"'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_evidence = []
            for file in files:
                print(f"Processing file: {file.name}, size: {file.size}")
                evidence = HazardEvidence.objects.create(
                    hazard=hazard,
                    evidence_type=evidence_type,
                    image=file,
                    description=description,
                    uploaded_by=request.user
                )
                uploaded_evidence.append(evidence)
                print(f"Created evidence ID: {evidence.id}")
            
            serializer = HazardEvidenceSerializer(uploaded_evidence, many=True)
            print(f"Upload successful, returning {len(uploaded_evidence)} evidence items")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error in upload_evidence: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Upload failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign hazard to department or user"""
        hazard = self.get_object()
        serializer = HazardAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            # Update hazard with assignment data
            if serializer.validated_data.get('assigned_to'):
                hazard.assigned_to = serializer.validated_data['assigned_to']
            if serializer.validated_data.get('assigned_department'):
                hazard.assigned_department = serializer.validated_data['assigned_department']
            if serializer.validated_data.get('target_completion_date'):
                hazard.target_completion_date = serializer.validated_data['target_completion_date']
            
            # Update status to ManagerAssignment
            hazard.status = 'ManagerAssignment'
            hazard.reviewed_by = request.user
            hazard.save()
            
            # TODO: Send notification to assigned user/department
            
            response_serializer = HazardIdentificationSerializer(hazard)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update hazard status"""
        hazard = self.get_object()
        serializer = HazardStatusUpdateSerializer(
            data=request.data, 
            context={'instance': hazard}
        )
        
        if serializer.is_valid():
            old_status = hazard.status
            hazard.status = serializer.validated_data['status']
            
            # Set completion date if status is Done
            if hazard.status == 'Done' and not hazard.actual_completion_date:
                hazard.actual_completion_date = timezone.now()
            
            hazard.save()
            
            # TODO: Send notification about status change
            
            response_serializer = HazardIdentificationSerializer(hazard)
            return Response({
                'message': f'Status updated from {old_status} to {hazard.status}',
                'hazard': response_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def inspector_assessment(self, request, pk=None):
        """Inspector assessment of hazard - collect evidence and update status"""
        try:
            hazard = self.get_object()
            
            # Check if user is assigned to this hazard or is an inspector
            user = request.user
            user_role = None
            if hasattr(user, 'userprofile') and user.userprofile and user.userprofile.role:
                user_role = user.userprofile.role.name
            
            if not (hazard.assigned_to == user or (user_role and user_role.upper() in ['INSPECTOR'])):
                return Response(
                    {'error': 'You are not authorized to assess this hazard'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get assessment data
            assessment_notes = request.data.get('assessment_notes', '')
            risk_level = request.data.get('risk_level', '')
            recommended_actions = request.data.get('recommended_actions', '')
            new_status = request.data.get('status', 'InspectorReview')
            
            # Update hazard with assessment
            if assessment_notes:
                hazard.additional_notes = f"{hazard.additional_notes}\n\nInspector Assessment: {assessment_notes}".strip()
            
            if recommended_actions:
                hazard.recommended_controls = f"{hazard.recommended_controls}\n\nInspector Recommendations: {recommended_actions}".strip()
            
            # Update status
            old_status = hazard.status
            hazard.status = new_status
            hazard.reviewed_by = user
            hazard.save()
            
            return Response({
                'message': f'Hazard assessed successfully. Status updated from {old_status} to {hazard.status}',
                'hazard': HazardIdentificationSerializer(hazard).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Assessment failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for hazards"""
        queryset = self.get_queryset()
        
        stats = {
            'total_hazards': queryset.count(),
            'logged_hazards': queryset.filter(status='Logged').count(),
            'in_review_hazards': queryset.filter(status='InspectorReview').count(),
            'assigned_hazards': queryset.filter(status='ManagerAssignment').count(),
            'in_progress_hazards': queryset.filter(status='InProgress').count(),
            'completed_hazards': queryset.filter(status='Done').count(),
            'overdue_hazards': queryset.filter(
                target_completion_date__lt=timezone.now(),
                status__in=['Logged', 'InspectorReview', 'ManagerAssignment', 'InProgress']
            ).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def my_hazards(self, request):
        """Get hazards assigned to the current user"""
        user = request.user
        queryset = self.get_queryset().filter(
            Q(reported_by=user) | Q(assigned_to=user)
        )
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HazardIdentificationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HazardIdentificationListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """Get hazards pending manager review/assignment"""
        if request.user.role != 'MANAGER':
            return Response(
                {'error': 'Only managers can access this endpoint'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(
            status__in=['Logged', 'InspectorReview']
        )
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HazardIdentificationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = HazardIdentificationListSerializer(queryset, many=True)
        return Response(serializer.data)
