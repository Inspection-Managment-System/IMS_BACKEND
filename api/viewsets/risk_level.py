from django.utils.decorators import method_decorator
from django.db.models import Max
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers.issue_management import RiskLevelSerializer
from inspection_management.models import RiskLevel, DataGroup
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from api.mixins import DataGroupFilterMixin


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class RiskLevelViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    queryset = RiskLevel.objects.all()
    serializer_class = RiskLevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    data_group_field = 'group'
    apply_to_admin = True

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        group_id = data.get("group")
        if not data.get("order"):
            try:
                group_pk = int(group_id)
            except (TypeError, ValueError):
                group_pk = None

            if group_pk:
                max_order = (
                    RiskLevel.objects.filter(group_id=group_pk)
                    .aggregate(max_order=Max("order"))
                    .get("max_order")
                )
                data["order"] = (max_order + 1) if max_order is not None else 1
            else:
                data["order"] = 1

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        risk_level = serializer.save(changed_by=request.user)

        AuditHistory.objects.create(
            user=request.user, 
            action=f"Created risk level: {risk_level.name}"
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        risk_level = serializer.save(changed_by=request.user)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated risk level: {risk_level.name}"
        )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name

        AuditHistory.objects.create(
            user=request.user, 
            action=f"Deleted risk level: {name}"
        )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

