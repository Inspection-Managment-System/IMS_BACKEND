from django.utils.decorators import method_decorator
from rest_framework import permissions, viewsets
from api.serializers import TicketSerializer
from inspection_management.models import Ticket
from users.authorization import role_required
from users.models import User


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        user_profile = user.userprofile

        if user_profile.role.name == "Admin":
            return Ticket.objects.all()
        elif user_profile.role.name == "Manager":
            return Ticket.objects.filter(opened_by=user)
        elif user_profile.role.name == "Inspector":
            return Ticket.objects.filter(opened_by=user)

        return Ticket.objects.filter(opened_by=user)

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)