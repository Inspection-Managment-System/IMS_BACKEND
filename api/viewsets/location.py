from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import LocationSerializer
from inspection_management.models import DataGroup, Location
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Created location: {instance.name}"
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
            user=request.user,
            action=f"Updated location: {instance.name}"
        )

        return Response(serializer.data)

    def perform_destroy(self, instance):
        location_name = instance.name

        AuditHistory.objects.create(
            user=self.request.user,
            action=f"Deleted location: {location_name}"
        )

        instance.delete()

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "group" in data:
            data_group = DataGroup.objects.get(name=data.get("group"))
            data["group"] = data_group.id

        return data