from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import ComapnyGetSerializer, ComapnySerializer
from inspection_management.models import Company, DataGroup
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from api.mixins import DataGroupFilterMixin


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class CompanyViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = ComapnySerializer
    permission_classes = [permissions.IsAuthenticated]
    data_group_field = 'group'  # Filter by user's data groups
    apply_to_admin = True  # Admins are also filtered by their assigned data groups

    def list(self, request, *args, **kwargs):
        self.serializer_class = ComapnyGetSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ComapnyGetSerializer
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        company = self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user, action=f"Created company: {company.id} - {company.name}"
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
        updated_company = self.perform_update(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated company: {updated_company.id} - {updated_company.name}",
        )

        return Response(serializer.data)

    def perform_update(self, serializer):
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        company_id = instance.id
        company_name = instance.name

        AuditHistory.objects.create(
            user=request.user, action=f"Deleted company: {company_id} - {company_name}"
        )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "group" in data:
            group_name = data.get("group")
            data["group"] = DataGroup.objects.get(name=group_name).id
        return data

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request, *args, **kwargs):
        """
        Export all companies (filtered by data groups) as JSON.
        Uses the read serializer so group is represented by name.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ComapnyGetSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="import")
    def import_data(self, request, *args, **kwargs):
        """
        Import multiple companies in one request.
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
        required_fields = ["name", "description", "group"]

        for index, raw_item in enumerate(items):
            item = dict(raw_item)  # make a shallow copy

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
                company = serializer.save()
                created_ids.append(company.id)
                AuditHistory.objects.create(
                    user=request.user,
                    action=f"Imported company: {company.id} - {company.name}",
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
