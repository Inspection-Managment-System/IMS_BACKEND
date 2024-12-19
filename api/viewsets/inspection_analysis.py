from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import InspectionAnalysisSerializer
from ims_backend.utils.helper import \
    get_related_inspection_analyses_from_analysis_type
from inspection_management.models import (AnalysisType, DataGroup, Equipment,
                                          InspectionAnalysis, Location)
from users.authorization import role_required


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class InspectionAnalysisViewSet(viewsets.ModelViewSet):
    queryset = InspectionAnalysis.objects.all()
    serializer_class = InspectionAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        analysis_type_name = request.query_params.get("analysis_type", None)
        if analysis_type_name:
            related_inspection_analyses = (
                get_related_inspection_analyses_from_analysis_type(analysis_type_name)
            )
            self.queryset = related_inspection_analyses
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "group" in data:
            group_name = data.get("group")
            data["group"] = DataGroup.objects.get(name=group_name).id
        if "equipment" in data and data.get("equipment") != "":
            equipment_name = data.get("equipment")
            data["equipment"] = Equipment.objects.get(name=equipment_name).id
        if "analysis_type" in data:
            analysis_type_name = data.get("analysis_type")
            data["analysis_type"] = AnalysisType.objects.get(name=analysis_type_name).id
        if "location" in data:
            location_name = data.get("location")
            data["location"] = Location.objects.get(name=location_name).id
        return data
