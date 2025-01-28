from django.utils.decorators import method_decorator
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        unread_count = self.queryset.filter(is_read=False).count()

        serialized_data = self.get_serializer(self.queryset, many=True).data

        response_data = {"unread_count": unread_count, "notifications": serialized_data}

        return Response(response_data)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="mark_as_read")
    def mark_as_read(self, request, *args, **kwargs):
        notification_ids = request.data.get("ids", [])
        if not notification_ids:
            return Response(
                {"detail": "No notification IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notifications = Notification.objects.filter(
            id__in=notification_ids, recipient=request.user
        )
        updated_count = notifications.update(is_read=True)

        return Response(
            {"detail": f"{updated_count} notifications marked as read."},
            status=status.HTTP_200_OK,
        )
