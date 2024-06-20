import json
from datetime import datetime

from django.contrib.auth import authenticate, login
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserSerializer
from ims_backend.utils.jwt_token import generate_token
from ims_backend.utils.license import decrypt


class LicenseRequiredMixin:
    def validate_license(self):
        try:
            with open("license_v1.json", "rb") as file:
                encrypted_data = file.read()
                decrypted_data = decrypt(encrypted_data)
                license_data = json.loads(decrypted_data)
                expiration_date_str = license_data.get("expiration_date")
                if expiration_date_str:
                    expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
                    current_date = datetime.now()
                    if current_date > expiration_date:
                        return False
                    return True
                return False
        except Exception as e:
            print(f"License validation error: {str(e)}")
            return False


class CustomLoginView(LicenseRequiredMixin, APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if not self.validate_license():
            return Response(
                {"error": "Your license is either missing or expired."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user is not None:
            if not user.is_active:
                return Response(
                    {"error": "The user is inactive, because your license is limited."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            login(request, user)
            token = generate_token(user)
            user_profile_data = UserSerializer(user).data

            return Response(
                {
                    "user_data": user_profile_data,
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid Credentials or your account is inactive."},
            status=status.HTTP_400_BAD_REQUEST,
        )
