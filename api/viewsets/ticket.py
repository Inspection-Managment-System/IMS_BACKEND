from django.utils.decorators import method_decorator
from rest_framework import permissions, viewsets
from api.serializers import TicketSerializer
from inspection_management.models import Ticket
from users.authorization import role_required


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Ticket.objects.all()

    def get_queryset(self):
        user = self.request.user
        user_profile = user.userprofile

        if user_profile.role.name in ["Manager", "Inspector"]:
            return self.queryset.filter(opened_by=user)

        return self.queryset

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)