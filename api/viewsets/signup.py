from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from inspection_management.models import DataGroup
from users.models import UserProfile

from ..serializers import UserCreationSerializer, UserSerializer

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class SignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserCreationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                data_group_instance = DataGroup.objects.filter(
                    name=request.data.get("data_group")
                ).first()
                role_instance = Group.objects.filter(
                    name=request.data.get("role")
                ).first()
                UserProfile.objects.create(
                    user=user,
                    data_group=data_group_instance,
                    role=role_instance,
                    profile_picture=request.data.get(
                        "profile_picture", "static/images/avatars/1.png"
                    ),
                )
                token = get_tokens_for_user(user)
                return Response(
                    {"user": UserSerializer(user).data, "token": token},
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
