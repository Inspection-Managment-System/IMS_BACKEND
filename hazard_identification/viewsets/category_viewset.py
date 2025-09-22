from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from hazard_identification.models import HazardCategory
from hazard_identification.serializers import HazardCategorySerializer


class HazardCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing hazard categories"""
    
    queryset = HazardCategory.objects.filter(is_active=True)
    serializer_class = HazardCategorySerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter categories based on user permissions"""
        queryset = HazardCategory.objects.filter(is_active=True)
        
        # Add search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                name__icontains=search
            )
        
        return queryset.order_by('name')
    
    @action(detail=False, methods=['get'])
    def active_categories(self, request):
        """Get all active categories for dropdowns"""
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        """Soft delete - mark as inactive instead of deleting"""
        instance.is_active = False
        instance.save()
        
        return Response(
            {'message': 'Category deactivated successfully'}, 
            status=status.HTTP_200_OK
        )
