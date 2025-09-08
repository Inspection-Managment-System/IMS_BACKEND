from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from inspection_management.models.hse_result import HSEResult
from api.serializers.hse_result import HSEResultSerializer
from users.authorization import role_required
from django.utils.decorators import method_decorator


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class HSEResultViewSet(viewsets.ModelViewSet):
    queryset = HSEResult.objects.all().order_by("-entered_at")
    serializer_class = HSEResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter results based on user role and permissions"""
        user = self.request.user
        user_profile = user.userprofile
        
        # Start with base queryset
        queryset = self.queryset
        
        # Apply role-based filtering
        if user_profile.role.name == "Inspector":
            # Inspectors can only see their own results
            queryset = queryset.filter(entered_by=user)
        elif user_profile.role.name == "Manager":
            # Managers can see results for evinces they review
            queryset = queryset.filter(evince__reviewed_by=user)
        # Admins can see all results (no additional filtering)
        
        # Apply evince filter if provided
        evince_id = self.request.query_params.get('evince', None)
        if evince_id:
            queryset = queryset.filter(evince_id=evince_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the entered_by field to the current user"""
        serializer.save(entered_by=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='submit')
    def submit_result(self, request, pk=None):
        """Submit HSE result for review"""
        hse_result = self.get_object()
        
        if hse_result.status != 'draft':
            return Response(
                {"error": "Result has already been submitted"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hse_result.status = 'submitted'
        hse_result.save()
        
        return Response(
            {"message": "HSE result submitted successfully"}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_result(self, request, pk=None):
        """Approve HSE result (Manager only)"""
        hse_result = self.get_object()
        
        if request.user.userprofile.role.name != "Manager":
            return Response(
                {"error": "Only managers can approve results"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        hse_result.status = 'approved'
        hse_result.save()
        
        # Update the evince status
        hse_result.evince.status = 'Approved'
        hse_result.evince.save()
        
        return Response(
            {"message": "HSE result approved successfully"}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_result(self, request, pk=None):
        """Reject HSE result (Manager only)"""
        hse_result = self.get_object()
        
        if request.user.userprofile.role.name != "Manager":
            return Response(
                {"error": "Only managers can reject results"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        hse_result.status = 'rejected'
        hse_result.save()
        
        # Update the evince status
        hse_result.evince.status = 'Rejected'
        hse_result.evince.save()
        
        return Response(
            {"message": "HSE result rejected successfully"}, 
            status=status.HTTP_200_OK
        )
