from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from users.authorization import role_required
from inspection_management.models.hse_planner import HSEPlanner
from api.serializers.hse_planner import HSEPlannerSerializer, HSEPlannerListSerializer


@method_decorator(role_required(allowed_roles=["Admin", "Manager"]), name="dispatch")
class HSEPlannerViewSet(viewsets.ModelViewSet):
    """ViewSet for HSE Risk Assessment Planner"""
    queryset = HSEPlanner.objects.all().order_by('-changed_on')
    serializer_class = HSEPlannerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HSEPlannerListSerializer
        return HSEPlannerSerializer
    
    def preprocess_data(self, data):
        """Preprocess request data before validation - REMOVED, let serializer handle it"""
        # The serializer already has proper field mappings with _id suffixes
        # Just return data as-is
        return data
    
    def create(self, request, *args, **kwargs):
        """Create new HSE planner"""
        try:
            data = self.preprocess_data(request.data)
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            planner = serializer.save(changed_by=request.user)
            return Response(
                HSEPlannerSerializer(planner, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update HSE planner"""
        try:
            instance = self.get_object()
            data = self.preprocess_data(request.data)
            serializer = self.get_serializer(instance, data=data, partial=kwargs.get('partial', False))
            serializer.is_valid(raise_exception=True)
            planner = serializer.save(changed_by=request.user)
            return Response(HSEPlannerSerializer(planner, context={'request': request}).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete HSE planner"""
        instance = self.get_object()
        instance.delete()
        return Response({"message": "HSE Planner deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

