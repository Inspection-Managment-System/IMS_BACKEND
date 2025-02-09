from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import get_random_string
from django.utils.html import format_html
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

            self.send_password_reset_email(email, temporary_password)

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

    def send_password_reset_email(self, user_email, temporary_password):
        subject = "🔒 Password Reset Request"
        from_email = "no-reply@example.com"
        recipient_list = [user_email]

        text_content = f"Your temporary password is: {temporary_password}"

        html_content = format_html(
            """
            <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 500px; background: #ffffff; padding: 20px; 
                            border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                    <h2 style="color: #333;">🔒 Password Reset Request</h2>
                    <p>Dear User,</p>
                    <p>We have received a request to reset your password. Please use the temporary password below to log in:</p>
                    <div style="background: #eee; padding: 10px; font-size: 18px; 
                                font-weight: bold; text-align: center; border-radius: 5px;">
                        <strong>{}</strong>
                    </div>
                    <p>After logging in, we strongly recommend changing your password immediately for security reasons.</p>
                    <p style="margin-top: 20px;">Best Regards, <br> <strong>Inspection Management Support Team</strong></p>
                </div>
            </div>
            """,
            temporary_password,
        )

        email = EmailMultiAlternatives(
            subject, text_content, from_email, recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
