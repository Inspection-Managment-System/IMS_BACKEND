from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from inspection_management.models.maintenance_result import MaintenanceResult
from api.serializers.maintenance_result import MaintenanceResultSerializer


class MaintenanceResultViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceResult.objects.all()
    serializer_class = MaintenanceResultSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['evince__name', 'maintenance_actions_taken', 'additional_notes']
    ordering_fields = ['entered_at', 'maintenance_start_time', 'maintenance_end_time']
    ordering = ['-entered_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        evince_id = self.request.query_params.get('evince', None)
        if evince_id:
            queryset = queryset.filter(evince_id=evince_id)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='by-evince/(?P<evince_id>[^/.]+)')
    def by_evince(self, request, evince_id=None):
        """Get maintenance results for a specific evince"""
        results = self.get_queryset().filter(evince_id=evince_id)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='submit')
    def submit_maintenance_result(self, request, pk=None):
        """Submit maintenance result for review"""
        maintenance_result = self.get_object()
        maintenance_result.status = 'submitted'
        maintenance_result.save()
        
        return Response({
            'message': 'Maintenance result submitted successfully',
            'status': maintenance_result.status
        }, status=status.HTTP_200_OK)
