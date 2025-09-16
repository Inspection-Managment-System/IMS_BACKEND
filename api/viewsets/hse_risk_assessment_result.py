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
