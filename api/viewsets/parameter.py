from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import ParameterSerializer
from inspection_management.models import (AnalysisType, DataGroup,
                                          InspectionAnalysis, Parameter, Unit)
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class ParameterViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user, action=f"Created parameter: {instance.name}"
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
            user=request.user, action=f"Updated parameter: {instance.name}"
        )

        return Response(serializer.data)

    def perform_destroy(self, instance):
        parameter_name = instance.name

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted parameter: {parameter_name}"
        )

        instance.delete()

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "min_value" in data and data["min_value"] == "":
            data["min_value"] = None
        if "max_value" in data and data["max_value"] == "":
            data["max_value"] = None
        if "avg_value" in data and data["avg_value"] == "":
            data["avg_value"] = None
        if "group" in data:
            group_name = data.get("group")
            data["group"] = DataGroup.objects.get(name=group_name).id
        if "inspection_analysis" in data:
            inspection_analysis_name = data.get("inspection_analysis")
            data["inspection_analysis"] = InspectionAnalysis.objects.get(
                name=inspection_analysis_name
            ).id
        if "unit" in data:
            unit_name = data.get("unit")
            data["unit"] = Unit.objects.get(name=unit_name).id

        return data
