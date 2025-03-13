from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import PlannerSerializer
from inspection_management.models import (BusinessUnit, InspectionAnalysis,
                                          InspectionPoint, Planner)
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class PlannerViewSet(viewsets.ModelViewSet):
    queryset = Planner.objects.all()
    serializer_class = PlannerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer.instance.save()

        AuditHistory.objects.create(
            user=request.user, action=f"Created planner: {serializer.instance.id}"
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        instance = self.get_object()
        data = self.preprocess_data(data)

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        AuditHistory.objects.create(
            user=request.user, action=f"Updated planner: {instance.id}"
        )

        return Response(serializer.data)

    def perform_destroy(self, instance):
        planner_id = instance.id

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted planner: {planner_id}"
        )

        instance.delete()

    def preprocess_data(self, data):
        if "month" in data:
            data["month"] = ",".join(data.pop("month"))

        if "description" in data:
            data["evince_description"] = data.get("description")

        if "crtical_instructions" in data:
            data["attachment"] = data.get("crtical_instructions")

        if "crtical_instructions_file_name" in data:
            data["attachment_name"] = data.get("crtical_instructions_file_name")

        if "business_unit" in data:
            business_unit_name = data.get("business_unit")
            data["evince_business_unit"] = BusinessUnit.objects.get(
                name=business_unit_name
            ).id

        if "inspection_point" in data:
            inspection_point_name = data.get("inspection_point")
            data["evince_inspection_point"] = InspectionPoint.objects.get(
                name=inspection_point_name
            ).id

        if "inspection_analyses" in data:
            inspection_analysis_names = data.get("inspection_analyses")
            data["evince_inspection_analyses"] = inspection_analysis_names
            for index, inspection_analysis_name in enumerate(inspection_analysis_names):
                data["evince_inspection_analyses"][index] = (
                    InspectionAnalysis.objects.get(name=inspection_analysis_name).id
                )

        return data
