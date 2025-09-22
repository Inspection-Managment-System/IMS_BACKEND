from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from users.models.user import User


class HazardUserViewSet(viewsets.ViewSet):
    """ViewSet for getting users by role for hazard assignment"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='managers')
    def get_managers(self, request):
        """Get all users with Manager role"""
        try:
            # Try both case variations
            manager_groups = Group.objects.filter(name__in=['Manager', 'MANAGER'])
            managers = User.objects.filter(
                userprofile__role__in=manager_groups
            ).select_related('userprofile')
            
            manager_data = []
            for manager in managers:
                manager_data.append({
                    'id': manager.id,
                    'username': manager.username,
                    'email': manager.email,
                    'first_name': manager.first_name,
                    'last_name': manager.last_name,
                    'full_name': f"{manager.first_name} {manager.last_name}".strip() or manager.username
                })
            
            return Response(manager_data)
        except Group.DoesNotExist:
            return Response(
                {'error': 'Manager role group not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch managers: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='inspectors')
    def get_inspectors(self, request):
        """Get all users with Inspector role"""
        try:
            # Try both case variations
            inspector_groups = Group.objects.filter(name__in=['Inspector', 'INSPECTOR'])
            inspectors = User.objects.filter(
                userprofile__role__in=inspector_groups
            ).select_related('userprofile')
            
            inspector_data = []
            for inspector in inspectors:
                inspector_data.append({
                    'id': inspector.id,
                    'username': inspector.username,
                    'email': inspector.email,
                    'first_name': inspector.first_name,
                    'last_name': inspector.last_name,
                    'full_name': f"{inspector.first_name} {inspector.last_name}".strip() or inspector.username
                })
            
            return Response(inspector_data)
        except Group.DoesNotExist:
            return Response(
                {'error': 'Inspector role group not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch inspectors: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
