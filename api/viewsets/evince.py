from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import EvinceSerializer
from inspection_management.models import (BusinessUnit, Evince,
                                          InspectionAnalysis, InspectionPoint,
                                          InspectionResult, InspectionTest)
from users.authorization import role_required
from users.models import User


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class EvinceViewSet(viewsets.ModelViewSet):
    queryset = Evince.objects.all()
    serializer_class = EvinceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer.instance.save()
        self.create_inspection_tests_and_results(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def create_inspection_tests_and_results(self, evince):
        for inspection_analysis in evince.inspection_analyses.all():
            inspection_test = InspectionTest.objects.create(
                evince=evince,
                inspection_analysis=inspection_analysis,
                changed_by=evince.changed_by,
            )
            InspectionResult.objects.create(
                evince=evince,
                inspection_test=inspection_test,
                changed_by=evince.changed_by,
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
        if "business_unit" in data:
            business_unit_name = data.get("business_unit")
            data["business_unit"] = BusinessUnit.objects.get(name=business_unit_name).id
        if "inspection_point" in data:
            inspection_point_name = data.get("inspection_point")
            data["inspection_point"] = InspectionPoint.objects.get(
                name=inspection_point_name
            ).id
        if "inspection_analyses" in data:
            inspection_analysis_names = data.get("inspection_analyses")
            for index, inspection_analysis_name in enumerate(inspection_analysis_names):
                data["inspection_analyses"][index] = InspectionAnalysis.objects.get(
                    name=inspection_analysis_name
                ).id
        return data
