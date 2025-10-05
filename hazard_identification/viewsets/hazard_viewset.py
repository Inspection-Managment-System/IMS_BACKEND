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
            # Manager can see:
            # 1. Hazards assigned to them specifically
            # 2. Hazards that have been assessed by inspectors (where inspectors have entered results)
            queryset = queryset.filter(
                Q(assigned_to=user) |  # Hazards assigned to this manager
                Q(status__in=['ManagerReview', 'Approved', 'Rejected', 'Reassigned'])  # Hazards assessed by inspectors
            )
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
            
            if evidence_type not in ['before', 'after', 'initial', 'admin', 'assessment', 'inspector']:
                return Response(
                    {'error': 'Evidence type must be one of: before, after, initial, admin, assessment, inspector'}, 
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
            risk_level = request.data.get('risk_level', '')
            risk_factors = request.data.get('risk_factors', '')
            exposure_assessment = request.data.get('exposure_assessment', '')
            root_cause_analysis = request.data.get('root_cause_analysis', '')
            immediate_risks = request.data.get('immediate_risks', '')
            potential_consequences = request.data.get('potential_consequences', '')
            immediate_actions = request.data.get('immediate_actions', '')
            long_term_solutions = request.data.get('long_term_solutions', '')
            preventive_measures = request.data.get('preventive_measures', '')
            overall_assessment = request.data.get('overall_assessment', '')
            confidence_level = request.data.get('confidence_level', '')
            next_steps = request.data.get('next_steps', '')
            new_status = request.data.get('status', 'InspectorReview')
            
            # Build comprehensive assessment notes
            assessment_notes = []
            if risk_factors:
                assessment_notes.append(f"Risk Factors: {risk_factors}")
            if exposure_assessment:
                assessment_notes.append(f"Exposure Assessment: {exposure_assessment}")
            if root_cause_analysis:
                assessment_notes.append(f"Root Cause Analysis: {root_cause_analysis}")
            if immediate_risks:
                assessment_notes.append(f"Immediate Risks: {immediate_risks}")
            if potential_consequences:
                assessment_notes.append(f"Potential Consequences: {potential_consequences}")
            if overall_assessment:
                assessment_notes.append(f"Overall Assessment: {overall_assessment}")
            if confidence_level:
                assessment_notes.append(f"Confidence Level: {confidence_level}")
            if next_steps:
                assessment_notes.append(f"Next Steps: {next_steps}")
            
            # Update hazard with comprehensive assessment
            if assessment_notes:
                comprehensive_assessment = "\n\n".join(assessment_notes)
                hazard.additional_notes = f"{hazard.additional_notes}\n\n=== INSPECTOR ASSESSMENT ===\n{comprehensive_assessment}".strip()
            
            # Update recommended controls with detailed actions
            recommended_controls = []
            if immediate_actions:
                recommended_controls.append(f"IMMEDIATE ACTIONS: {immediate_actions}")
            if long_term_solutions:
                recommended_controls.append(f"LONG-TERM SOLUTIONS: {long_term_solutions}")
            if preventive_measures:
                recommended_controls.append(f"PREVENTIVE MEASURES: {preventive_measures}")
            
            if recommended_controls:
                comprehensive_controls = "\n\n".join(recommended_controls)
                hazard.recommended_controls = f"{hazard.recommended_controls}\n\n=== INSPECTOR RECOMMENDATIONS ===\n{comprehensive_controls}".strip()
            
            # Update risk level if provided
            if risk_level:
                hazard.severity_level = risk_level
            
            # Update status
            old_status = hazard.status
            hazard.status = 'ManagerReview'  # Always go to manager review after inspector assessment
            hazard.reviewed_by = user
            hazard.save()
            
            # Send lightweight email notification to manager (non-blocking)
            try:
                from hazard_identification.services.email_notifications import HazardEmailNotificationService
                HazardEmailNotificationService.send_assessment_completion_notification(hazard, user)
            except Exception as e:
                # Log error but don't fail the main request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send assessment notification: {str(e)}")
            
            return Response({
                'message': f'Hazard assessed successfully. Status updated from {old_status} to {hazard.status}',
                'hazard': HazardIdentificationSerializer(hazard).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Assessment failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def manager_review(self, request, pk=None):
        """Manager review of hazard assessment - approve, reject, or reassign"""
        try:
            hazard = self.get_object()
            
            # Check if user is a manager
            user = request.user
            user_role = None
            if hasattr(user, 'userprofile') and user.userprofile and user.userprofile.role:
                user_role = user.userprofile.role.name
            
            if not (user_role and user_role.upper() in ['MANAGER']):
                return Response(
                    {'error': 'You are not authorized to review hazards'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get review data
            decision = request.data.get('decision', '')
            review_notes = request.data.get('review_notes', '')
            rejection_reason = request.data.get('rejection_reason', '')
            reassignment_notes = request.data.get('reassignment_notes', '')
            
            if not decision:
                return Response(
                    {'error': 'Decision is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update hazard with manager review
            old_status = hazard.status
            hazard.manager_decision = decision
            hazard.manager_review_notes = review_notes
            hazard.reviewed_by = user
            
            if decision == 'Approved':
                hazard.status = 'Approved'
            elif decision == 'Rejected':
                hazard.status = 'Rejected'
                hazard.rejection_reason = rejection_reason
            elif decision == 'Reassigned':
                hazard.status = 'Reassigned'
                hazard.reassignment_notes = reassignment_notes
                # You might want to reassign to a different inspector here
            
            hazard.save()
            
            # Send lightweight email notification for status update (non-blocking)
            try:
                from hazard_identification.services.email_notifications import HazardEmailNotificationService
                HazardEmailNotificationService.send_status_update_notification(hazard, old_status, hazard.status, user)
            except Exception as e:
                # Log error but don't fail the main request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send status notification: {str(e)}")
            
            return Response({
                'message': f'Hazard {decision.lower()} successfully. Status updated from {old_status} to {hazard.status}',
                'hazard': HazardIdentificationSerializer(hazard).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Review failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for hazards"""
        queryset = self.get_queryset()
        
        stats = {
            'total_hazards': queryset.count(),
            'logged_hazards': queryset.filter(status='Logged').count(),
            'assigned_to_inspector': queryset.filter(status='AssignedToInspector').count(),
            'inspector_assessment': queryset.filter(status='InspectorAssessment').count(),
            'manager_review': queryset.filter(status='ManagerReview').count(),
            'approved_hazards': queryset.filter(status='Approved').count(),
            'rejected_hazards': queryset.filter(status='Rejected').count(),
            'reassigned_hazards': queryset.filter(status='Reassigned').count(),
            'in_progress_hazards': queryset.filter(status='InProgress').count(),
            'completed_hazards': queryset.filter(status='Completed').count(),
            'overdue_hazards': queryset.filter(
                target_completion_date__lt=timezone.now(),
                status__in=['Logged', 'AssignedToInspector', 'InspectorAssessment', 'ManagerReview', 'InProgress']
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
