from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import DataGroupSerializer
from inspection_management.models import DataGroup
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class DatagroupViewSet(viewsets.ModelViewSet):
    queryset = DataGroup.objects.all()
    serializer_class = DataGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        For management (?for_management=true): Admins see ALL groups
        For assignment (?assignable=true or default): Users see only their ASSIGNED groups
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Check query parameter
        for_management = self.request.query_params.get('for_management', 'false').lower() == 'true'
        
        # If for_management=true: Admins see all groups (for Data Groups page)
        if for_management:
            if user.is_authenticated:
                if hasattr(user, 'userprofile') and user.userprofile.role:
                    if user.userprofile.role.name == 'Admin':
                        return queryset  # Admin sees all for management
            if user.is_superuser:
                return queryset
        
        # Default behavior: Return only assigned groups (for dropdowns/assignments)
        if hasattr(user, 'userprofile'):
            user_data_groups = user.userprofile.data_groups.all()
            return user_data_groups
        
        return queryset.none()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        datagroup = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Created data group: {datagroup.id} - {datagroup.name}",
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_group = self.perform_update(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated data group: {updated_group.id} - {updated_group.name}",
        )

        return Response(serializer.data)

    def perform_update(self, serializer):
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        group_id = instance.id
        group_name = instance.name

        AuditHistory.objects.create(
            user=request.user, action=f"Deleted data group: {group_id} - {group_name}"
        )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def preprocess_data(self, data):
        if "name" in data:
            data["name"] = data["name"].lower()
        return data
