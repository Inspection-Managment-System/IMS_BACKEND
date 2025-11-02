from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import InspectionPointSerializer
from ims_backend.utils import geodesic_algo, inspection_point_categorization
from ims_backend.utils.helper import \
    get_related_inspection_points_from_business_unit
from inspection_management.models import BusinessUnit, InspectionPoint
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from users.models.notification import Notification
from inspection_management.models.inspection_point import LocationRestrictionSetting
from api.mixins import DataGroupFilterMixin


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class InspectionPointViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    queryset = InspectionPoint.objects.all()
    serializer_class = InspectionPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    data_group_field = 'group'  # Filter by user's data groups
    apply_to_admin = True  # Admins are also filtered by their assigned data groups

    def list(self, request, *args, **kwargs):
        # Preserve existing business_unit filter logic
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
        inspection_point = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        AuditHistory.objects.create(
            user=self.request.user,
            action=f"Created inspection point: {inspection_point.id} - {inspection_point.name}",
        )

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
        original_name = instance.name
        original_business_unit_id = (
            instance.business_unit.id if instance.business_unit else None
        )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_inspection_point = self.perform_update(serializer)

        AuditHistory.objects.create(
            user=self.request.user,
            action=f"Updated inspection point: {updated_inspection_point.id} - {updated_inspection_point.name}",
        )

        return Response(serializer.data)

    def perform_update(self, serializer):
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        inspection_point_id = instance.id
        inspection_point_name = instance.name
        business_unit = instance.business_unit

        AuditHistory.objects.create(
            user=self.request.user,
            action=f"Deleted inspection point: {inspection_point_id} - {inspection_point_name}",
        )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    @action(detail=False, methods=["get"], url_path="check_user_location")
    def check_user_location(self, request, *args, **kwargs):
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        inspection_point_id = request.query_params.get("inspection_point_id")

        if not all([latitude, longitude, inspection_point_id]):
            return Response(
                {
                    "detail": "All parameters (latitude, longitude, inspection_point_id) are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Bypass location check if restriction is disabled
        if not LocationRestrictionSetting.get_flag():
            return Response({"is_user_at_location": True}, status=status.HTTP_200_OK)

        inspection_point = InspectionPoint.objects.get(id=inspection_point_id)
        target_coords = (inspection_point.latitude, inspection_point.longitude)
        user_coords = (latitude, longitude)

        is_user_at_location = geodesic_algo.is_user_at_location(
            target_coords, user_coords, 50
        )

        return Response(
            {"is_user_at_location": is_user_at_location}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="location_restriction_flag")
    def get_location_restriction_flag(self, request):
        """Returns the current state of the location restriction flag."""
        return Response({"is_enabled": LocationRestrictionSetting.get_flag()})

    @action(detail=False, methods=["post"], url_path="set_location_restriction_flag")
    def set_location_restriction_flag(self, request):
        """Sets the location restriction flag. Only Admins allowed."""
        if not request.user.is_superuser and not (hasattr(request.user, 'userprofile') and getattr(request.user.userprofile, 'role', None) and request.user.userprofile.role.name == 'Admin'):
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        is_enabled = request.data.get("is_enabled")
        if is_enabled is None:
            return Response({"detail": "is_enabled is required."}, status=status.HTTP_400_BAD_REQUEST)
        LocationRestrictionSetting.set_flag(bool(is_enabled))
        return Response({"is_enabled": LocationRestrictionSetting.get_flag()})
