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
        notification_id = request.data.get("id", None)
        if not notification_id:
            return Response(
                {"detail": "No notification ID provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if notification_id == "all":
            notifications = self.queryset.filter(recipient=request.user, is_read=False)
            notifications.update(is_read=True)
            return Response(
                {"detail": f"All Notifications marked as read."},
                status=status.HTTP_200_OK,
            )

        else:
            notification = Notification.objects.get(
                id=notification_id, recipient=request.user
            )
            notification.is_read = True
            notification.save()
            return Response(
                {"detail": "Notification marked as read."},
                status=status.HTTP_200_OK,
            )
