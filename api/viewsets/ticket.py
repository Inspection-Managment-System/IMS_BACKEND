from django.utils.decorators import method_decorator
from rest_framework import permissions, viewsets

from api.serializers import TicketSerializer
from inspection_management.models import Ticket
from users.authorization import role_required
from users.models.audit_history import AuditHistory
from users.models.notification import Notification


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
        ticket = serializer.save(opened_by=self.request.user)

        AuditHistory.objects.create(
            user=self.request.user, action=f"Created ticket: {ticket.id}"
        )

        try:
            from users.models import User, UserProfile

            admin_users = User.objects.filter(userprofile__role__name="Admin")

            for admin in admin_users:
                if admin != self.request.user:
                    Notification.objects.create(
                        sender=self.request.user,
                        recipient=admin,
                        content=f"New ticket #{ticket.id} has been created by {self.request.user.username}.",
                    )
        except Exception as e:
            print(f"Error sending admin notifications: {str(e)}")

    def perform_update(self, serializer):
        original_ticket = self.get_object()
        updated_ticket = serializer.save()

        AuditHistory.objects.create(
            user=self.request.user, action=f"Updated ticket: {updated_ticket.id}"
        )

        if original_ticket.opened_by != self.request.user:
            Notification.objects.create(
                sender=self.request.user,
                recipient=original_ticket.opened_by,
                content=f"Your ticket #{updated_ticket.id} has been updated.",
            )

    def perform_destroy(self, instance):
        ticket_id = instance.id
        ticket_owner = instance.opened_by

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted ticket: {ticket_id}"
        )

        if ticket_owner != self.request.user:
            Notification.objects.create(
                sender=self.request.user,
                recipient=ticket_owner,
                content=f"Your ticket #{ticket_id} has been deleted.",
            )

        instance.delete()
