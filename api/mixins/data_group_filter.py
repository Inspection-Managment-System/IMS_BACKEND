"""
Data Group Filtering Mixin
Automatically filters queryset by user's assigned data groups
"""
from rest_framework.response import Response
from rest_framework import status


class DataGroupFilterMixin:
    """
    Mixin to filter queryset by user's data groups.
    
    Usage:
        class CompanyViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
            queryset = Company.objects.all()
            data_group_field = 'group'  # Field name that references DataGroup
    """
    
    data_group_field = 'group'  # Default field name
    apply_to_admin = False  # If True, even Admin is filtered by data groups
    
    def get_queryset(self):
        """Override to filter by user's data groups"""
        queryset = super().get_queryset()
        
        # Get current user
        user = self.request.user
        
        # Skip filtering for anonymous users
        if user.is_anonymous:
            return queryset
        
        # Check if user has profile
        if not hasattr(user, 'userprofile'):
            return queryset.none()  # No profile = no access
        
        user_profile = user.userprofile
        
        # Check if user has role
        if not user_profile.role:
            return queryset.none()  # No role = no access
        
        # Admin sees all data (unless apply_to_admin = True)
        if user_profile.role.name == 'Admin' and not self.apply_to_admin:
            return queryset
        
        # Get user's data groups
        user_data_groups = user_profile.data_groups.all()
        
        if not user_data_groups.exists():
            return queryset.none()  # No data groups = no access
        
        # Filter by data groups
        filter_kwargs = {f'{self.data_group_field}__in': user_data_groups}
        return queryset.filter(**filter_kwargs).distinct()


class DataGroupAssignMixin:
    """
    Mixin to auto-assign data group when creating records.
    
    Usage:
        class CompanyViewSet(DataGroupAssignMixin, viewsets.ModelViewSet):
            data_group_field = 'group'
    """
    
    data_group_field = 'group'
    
    def perform_create(self, serializer):
        """Auto-assign data group if not provided"""
        
        # Check if data group is already set
        if self.data_group_field not in serializer.validated_data or \
           not serializer.validated_data.get(self.data_group_field):
            
            # Get user's primary or first data group
            user = self.request.user
            if hasattr(user, 'userprofile'):
                user_data_groups = user.userprofile.data_groups.all()
                if user_data_groups.exists():
                    # Use first data group (or primary if you add that field)
                    serializer.validated_data[self.data_group_field] = user_data_groups.first()
        
        return super().perform_create(serializer)


class DataGroupAccessMixin(DataGroupFilterMixin, DataGroupAssignMixin):
    """
    Complete data group access control mixin.
    Combines filtering (read) and auto-assignment (create).
    
    Usage:
        class CompanyViewSet(DataGroupAccessMixin, viewsets.ModelViewSet):
            queryset = Company.objects.all()
            data_group_field = 'group'
    """
    pass

