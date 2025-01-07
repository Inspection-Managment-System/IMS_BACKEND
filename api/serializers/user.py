from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from inspection_management.models import DataGroup
from users.models import UserProfile

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")


class DataGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataGroup
        fields = ("id", "name", "attachment_name", "attachment")


class UserProfileSerializer(serializers.ModelSerializer):
    role = GroupSerializer()
    data_groups = DataGroupSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ("role", "data_groups", "shift", "profile_picture")


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source="userprofile")

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "user_profile")


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
