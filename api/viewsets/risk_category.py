from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers.issue_management import RiskCategorySerializer
from inspection_management.models import RiskCategory, DataGroup
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from api.mixins import DataGroupFilterMixin


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class RiskCategoryViewSet(DataGroupFilterMixin, viewsets.ModelViewSet):
    queryset = RiskCategory.objects.all()
    serializer_class = RiskCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    data_group_field = 'group'
    apply_to_admin = True

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        risk_category = serializer.save(changed_by=request.user)

        AuditHistory.objects.create(
            user=request.user, 
            action=f"Created risk category: {risk_category.name}"
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        risk_category = serializer.save(changed_by=request.user)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated risk category: {risk_category.name}"
        )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name

        AuditHistory.objects.create(
            user=request.user, 
            action=f"Deleted risk category: {name}"
        )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

