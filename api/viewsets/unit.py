from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import UnitSerializer
from inspection_management.models import DataGroup, Unit
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from api.mixins import DataGroupFilterMixin


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class UnitViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    data_group_field = 'group'  # Filter by user's data groups
    apply_to_admin = True  # Admins are also filtered by their assigned data groups

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user, action=f"Created unit: {instance.name}"
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
        self.perform_update(serializer)

        AuditHistory.objects.create(
            user=request.user, action=f"Updated unit: {instance.name}"
        )

        return Response(serializer.data)

    def perform_destroy(self, instance):
        unit_name = instance.name

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted unit: {unit_name}"
        )

        instance.delete()

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "group" in data:
            group_name = data.get("group")
            data["group"] = DataGroup.objects.get(name=group_name).id
        return data

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request, *args, **kwargs):
        """
        Export all units (filtered by data groups) as JSON.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
