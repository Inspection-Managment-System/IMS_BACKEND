from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.models.audit_history import AuditHistory
from users.models.notification import Notification


class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            user = User.objects.get(email=email)

            temporary_password = get_random_string(length=8)

            user.set_password(temporary_password)
            user.save()

            send_mail(
                "Password Reset Request",
                f"Your temporary password is: {temporary_password}",
                "from@example.com",
                [email],
                fail_silently=False,
            )

            AuditHistory.objects.create(
                user=user, action="Password reset with temporary password"
            )

            Notification.objects.create(
                sender=user,
                recipient=user,
                content="Your password has been reset. Check your email for the temporary password.",
            )

            return Response(
                {"detail": "Password reset email has been sent."},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"detail": "No user is associated with this email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
