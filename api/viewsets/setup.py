from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.serializers.setup_serializer import SetupSerializer
from api.services.setup_service import initialize_system, check_setup_status
from users.models import SystemSettings


class SetupStatusView(APIView):
    """Check if system setup is needed"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get setup status"""
        status_data = check_setup_status()
        return Response(status_data)


class SetupInitializeView(APIView):
    """Initialize system with first admin user"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Perform first-time setup"""
        
        # Check if setup already completed
        if SystemSettings.is_setup_completed():
            return Response(
                {'error': 'Setup already completed'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate input
        serializer = SetupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Initialize system
            result = initialize_system(serializer.validated_data)
            
            return Response({
                'success': True,
                'message': 'Setup completed successfully!',
                'user': {
                    'email': result['user'].email,
                    'name': result['user'].get_full_name()
                },
                'organization': result['data_group'].name
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

