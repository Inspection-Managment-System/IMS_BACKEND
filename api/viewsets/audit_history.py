from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers.audit_history import AuditHistorySerializer
from users.authorization import role_required
from users.models.audit_history import AuditHistory


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class AuditHistoryViewSet(viewsets.ModelViewSet):
    queryset = AuditHistory.objects.all()
    serializer_class = AuditHistorySerializer
    permission_classes = [IsAuthenticated]
