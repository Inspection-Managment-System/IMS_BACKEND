from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import SiteSerializer
from ims_backend.utils.helper import get_related_sites_from_company
from inspection_management.models import Company, Site
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        company_name = request.query_params.get("company", None)
        if company_name:
            related_sites = get_related_sites_from_company(company_name)
            self.queryset = related_sites
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user, action=f"Created site: {instance.name}"
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
            user=request.user, action=f"Updated site: {instance.name}"
        )

        return Response(serializer.data)

    def perform_destroy(self, instance):
        site_name = instance.name

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted site: {site_name}"
        )

        instance.delete()

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "company" in data:
            company = Company.objects.get(name=data.get("company"))
            data["group"] = company.group.id
            data["company"] = company.id

        return data
