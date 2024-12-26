from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User


class PasswordResetAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"
            send_mail(
                "Password Reset Request",
                f"You can reset your password using the following link: {reset_url}",
                "from@example.com",
                [email],
                fail_silently=False,
            )
            return Response(
                {"detail": "Password reset email has been sent."},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
