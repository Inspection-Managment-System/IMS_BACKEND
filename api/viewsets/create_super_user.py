from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from inspection_management.models import DataGroup
from users.models import User, UserProfile


class CreateSuperUserView(APIView):
    def get(self, _):
        try:
            username = "admin"
            email = "a@g.com"
            password = "admin"

            if User.objects.filter(username=username).exists():
                return Response(
                    {"error": "A user with this username already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "A user with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            encrypted_password = make_password(password)

            user = User.objects.create(
                username=username, email=email, password=encrypted_password
            )

            roles = ["Admin", "Inspector", "Manager"]
            for role in roles:
                Group.objects.get_or_create(name=role)

            data_group_instance = DataGroup.objects.create(name="System")

            user_profile = UserProfile.objects.create(
                user=user,
                role=Group.objects.first(),
            )
            user_profile.data_groups.add(data_group_instance)

            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "password": password,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
