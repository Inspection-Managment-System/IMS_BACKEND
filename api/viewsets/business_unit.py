from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import BusinessUnitSerializer
from ims_backend.utils.helper import get_related_business_units_from_site
from inspection_management.models import BusinessUnit, Site
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from api.mixins import DataGroupFilterMixin


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class BusinessUnitViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    queryset = BusinessUnit.objects.all()
    serializer_class = BusinessUnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    data_group_field = 'group'  # Filter by user's data groups
    apply_to_admin = True  # Admins are also filtered by their assigned data groups

    def list(self, request, *args, **kwargs):
        # Preserve existing site filter logic
        site_name = request.query_params.get("site", None)
        if site_name:
            related_business_units = get_related_business_units_from_site(site_name)
            self.queryset = related_business_units
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        business_unit = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Created business unit: {business_unit.id} - {business_unit.name}",
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
        updated_unit = self.perform_update(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated business unit: {updated_unit.id} - {updated_unit.name}",
        )

        return Response(serializer.data)

    def perform_update(self, serializer):
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        unit_id = instance.id
        unit_name = instance.name

        AuditHistory.objects.create(
            user=request.user, action=f"Deleted business unit: {unit_id} - {unit_name}"
        )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "site" in data:
            site = Site.objects.get(name=data.get("site"))
            data["group"] = site.group.id
            data["site"] = site.id

        return data
