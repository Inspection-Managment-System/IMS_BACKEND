from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SiteSerializer
from ims_backend.utils.helper import get_related_sites_from_company
from inspection_management.models import Company, Site
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from api.mixins import DataGroupFilterMixin


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class SiteViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    data_group_field = 'group'  # Filter by user's data groups
    apply_to_admin = True  # Admins are also filtered by their assigned data groups

    def list(self, request, *args, **kwargs):
        # Preserve existing company filter logic
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

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request, *args, **kwargs):
        """
        Export all sites (filtered by data groups / optional company) as JSON.
        """
        # Reuse existing list filtering, including company filter and data groups
        queryset = self.filter_queryset(self.get_queryset())

        # Apply the same company filter logic used in list()
        company_name = request.query_params.get("company", None)
        if company_name:
            queryset = get_related_sites_from_company(company_name)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="import")
    def import_data(self, request, *args, **kwargs):
        """
        Import multiple sites in one request.
        Accepts either a list of objects or {'items': [...]}.
        Does not modify schema or existing records.
        """
        payload = request.data

        if isinstance(payload, list):
            items = payload
        else:
            items = payload.get("items", [])

        if not isinstance(items, list):
            return Response(
                {"detail": "Expected a list of items or an 'items' key containing a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_ids = []
        errors = []
        required_fields = ["name", "description", "company"]

        for index, raw_item in enumerate(items):
            item = dict(raw_item)

            # High-level mandatory field check (useful for Excel imports)
            missing = [field for field in required_fields if not item.get(field)]
            if missing:
                errors.append(
                    {
                        "index": index,
                        "errors": {
                            "missing_required_fields": missing,
                            "detail": "One or more mandatory fields are missing or empty.",
                        },
                    }
                )
                continue

            item = self.preprocess_data(item)

            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                site = serializer.save()
                created_ids.append(site.id)
                AuditHistory.objects.create(
                    user=request.user,
                    action=f"Imported site: {site.id} - {site.name}",
                )
            else:
                errors.append({"index": index, "errors": serializer.errors})

        status_code = (
            status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS
        )

        return Response(
            {"created_ids": created_ids, "errors": errors},
            status=status_code,
        )
