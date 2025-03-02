from django.utils.decorators import method_decorator
from rest_framework import permissions, viewsets

from api.serializers import TicketSerializer
from inspection_management.models import Ticket
from users.authorization import role_required


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
