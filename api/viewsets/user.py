from django.contrib.auth.models import Group
from users.models import UserProfile
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.serializers import UserSerializer
from ims_backend.utils.helper import get_user_through_role
from inspection_management.models import DataGroup
from users.authorization import role_required
from users.models import User
from rest_framework.decorators import action



@method_decorator(
    role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch"
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_type = request.query_params.get("user_type", None)
        user_id = request.query_params.get("user_id", None)

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if hasattr(user, "userprofile") and user.userprofile:
                    request_user_data_groups = user.userprofile.data_groups.all()
                    self.queryset = self.queryset.filter(
                        userprofile__data_groups__in=request_user_data_groups
                    ).distinct()

                    self.queryset = self.queryset.exclude(id=user_id)

                else:
                    return Response(
                        {"detail": "UserProfile not found for the given user_id."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except User.DoesNotExist:
                return Response(
                    {"detail": "User not found with the given user_id."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if user_type:
            try:
                related_users = get_user_through_role(user_type)

                if isinstance(related_users, list):
                    related_user_ids = [user.id for user in related_users]
                    self.queryset = self.queryset.filter(id__in=related_user_ids)
                else:
                    self.queryset = self.queryset.filter(
                        id__in=related_users.values_list("id", flat=True)
                    )

            except Exception as e:
                return Response(
                    {
                        "detail": f"Error fetching users for user_type '{user_type}': {str(e)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()

        user_data = {"username": data.get("username"), "email": data.get("email")}
        user_profile_data = data.get("user_profile", {})

        try:
            with transaction.atomic():
                self.update_user_profile(instance.userprofile, user_profile_data)
                self.update_user(instance, user_data, partial)

                return Response(self.get_serializer(instance).data)
        except (Group.DoesNotExist, DataGroup.DoesNotExist) as e:
            raise ValidationError({"detail": str(e)})

    def update_user_profile(self, user_profile, data):
        updated = False

        if "role" in data:
            role_data = data.get("role")
            name = role_data.get("name")
            if name != "":
                user_profile.role = Group.objects.get(name=role_data.get("name"))
                updated = True

        if "data_group" in data:
            data_group_names = data.get("data_group", [])
            if data_group_names != []:
                data_group_instances = DataGroup.objects.filter(
                    name__in=data_group_names
                )
                user_profile.data_groups.set(data_group_instances)
                updated = True

        if "profile_picture" in data:
            if data.get("profile_picture") != "":
                user_profile.profile_picture = data.get("profile_picture")
                updated = True

        if updated:
            user_profile.save()

    def update_user(self, instance, data, partial):
        user_data = {k: v for k, v in data.items() if v is not None}
        if user_data:
            serializer = self.get_serializer(instance, data=user_data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

    @action(detail=False, methods=["get"], url_path="get_shifts")
    def get_all_shifts(self, request, *args, **kwargs):
        return Response(UserProfile.SHIFT_TIMINGS)
        

