from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import InspectionPointSerializer
from ims_backend.utils import inspection_point_categorization
from ims_backend.utils.helper import \
    get_related_inspection_points_from_business_unit
from inspection_management.models import BusinessUnit, InspectionPoint
from users.authorization import role_required


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class InspectionPointViewSet(viewsets.ModelViewSet):
    queryset = InspectionPoint.objects.all()
    serializer_class = InspectionPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        business_unit_name = request.query_params.get("business_unit", None)
        if business_unit_name:
            related_inspection_points = (
                get_related_inspection_points_from_business_unit(business_unit_name)
            )
            self.queryset = related_inspection_points
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
        if "business_unit" in data:
            business_unit = BusinessUnit.objects.get(name=data.get("business_unit"))
            data["group"] = business_unit.group.id
            data["business_unit"] = business_unit.id

        return data

    @action(detail=False, methods=["post"], url_path="categorize")
    def categorize(self, request, *args, **kwargs):
        flammability = request.data.get("flammability")
        health_risk = request.data.get("health_risk")
        reactivity = request.data.get("reactivity")

        if not all([flammability, health_risk, reactivity]):
            return Response(
                {
                    "detail": "All parameters (flammability, health_risk, reactivity) are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        overall_hazard_level = (
            inspection_point_categorization.categorize_inspection_point(
                flammability, health_risk, reactivity
            )
        )
        return Response(
            {"overall_hazard_level": overall_hazard_level}, status=status.HTTP_200_OK
        )
