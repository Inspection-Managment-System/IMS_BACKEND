from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import DataListSerializer
from inspection_management.models import DataList
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from api.mixins import DataGroupFilterMixin


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class DataListViewSet(viewsets.ModelViewSet):
    queryset = DataList.objects.all()
    serializer_class = DataListSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Note: DataList has no group field - shared across all data groups

    def list(self, request, *args, **kwargs):
        # Preserve existing pagination logic
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self._convert_data_field(serializer.data)
            return self.get_paginated_response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        response_data = self._convert_data_field(serializer.data)
        return Response(response_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = self._convert_data_field([serializer.data])
        return Response(response_data[0])

    def create(self, request, *args, **kwargs):
        result = self._handle_create_or_update(request, partial=False)

        datalist_id = result.data.get("id")
        datalist_name = result.data.get("name", "Unknown")

        AuditHistory.objects.create(
            user=request.user,
            action=f"Created data list: {datalist_id} - {datalist_name}",
        )

        return result

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        datalist_id = instance.id
        datalist_name = instance.name

        result = self._handle_create_or_update(
            request, partial=kwargs.pop("partial", False)
        )

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated data list: {datalist_id} - {datalist_name}",
        )

        return result

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        datalist_id = instance.id
        datalist_name = instance.name

        AuditHistory.objects.create(
            user=request.user,
            action=f"Deleted data list: {datalist_id} - {datalist_name}",
        )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _handle_create_or_update(self, request, partial):
        data = self.preprocess_data(request.data.copy())
        instance = self.get_object() if partial else None
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if partial:
            self.perform_update(serializer)
        else:
            self.perform_create(serializer)

        response_data = self._convert_data_field([serializer.data])
        return Response(
            response_data[0] if partial else serializer.data,
            status=status.HTTP_200_OK if partial else status.HTTP_201_CREATED,
        )

    def preprocess_data(self, data):
        if "data" in data and isinstance(data["data"], list):
            data["data"] = ",".join(data["data"])
        return data

    def _convert_data_field(self, data):
        for item in data:
            if "data" in item and item["data"]:
                item["data"] = item["data"].split(",")
        return data

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request, *args, **kwargs):
        """
        Export all data lists as JSON.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = self._convert_data_field(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)
