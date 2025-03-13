from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import EquipmentTypeSerializer
from inspection_management.models import DataGroup, EquipmentType
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class EquipmentTypeViewSet(viewsets.ModelViewSet):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        equipment_type = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Created equipment type: {equipment_type.id} - {equipment_type.name}",
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
        updated_type = self.perform_update(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated equipment type: {updated_type.id} - {updated_type.name}",
        )

        return Response(serializer.data)

    def perform_update(self, serializer):
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        type_id = instance.id
        type_name = instance.name

        AuditHistory.objects.create(
            user=request.user, action=f"Deleted equipment type: {type_id} - {type_name}"
        )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "group" in data:
            data_group = DataGroup.objects.get(name=data.get("group"))
            data["group"] = data_group.id

        return data
