from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.models.audit_history import AuditHistory
from users.models.notification import Notification


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            new_password = request.data.get("new_password")
            temporary_password = request.data.get("temporary_password")

            user = User.objects.get(email=email)

            user = authenticate(
                request, username=user.username, password=temporary_password
            )

            if user is not None:
                user.set_password(new_password)
                user.save()

                AuditHistory.objects.create(
                    user=user, action="Password changed successfully"
                )

                Notification.objects.create(
                    sender=user,
                    recipient=user,
                    content="Your password has been changed successfully.",
                )

                return Response(
                    {"detail": "Password has been changed successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Authentication failed. Incorrect temporary password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"detail": "No user is associated with this email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
