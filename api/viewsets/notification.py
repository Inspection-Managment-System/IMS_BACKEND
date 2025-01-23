from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers.notification import NotificationSerializer
from users.authorization import role_required
from users.models.notification import Notification


@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-id")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if "user_id" in request.query_params:
            user_id = request.query_params["user_id"]
            self.queryset = self.queryset.filter(recipient_id=user_id)
        return super().list(request, *args, **kwargs)
