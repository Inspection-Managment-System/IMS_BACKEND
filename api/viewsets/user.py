from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.serializers import UserSerializer
from ims_backend.utils.helper import get_user_through_role
from ims_backend.utils.inspection_point_data_utils import (
    get_user_location, sort_evinces_by_distance)
from inspection_management.models import DataGroup, Evince
from users.authorization import role_required
from users.models import User, UserProfile
from users.models.audit_history import AuditHistory


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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            AuditHistory.objects.create(
                user=request.user, action=f"Created user: {response.data['username']}"
            )

        return response

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        original_username = instance.username

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()

        user_data = {"username": data.get("username"), "email": data.get("email")}
        user_profile_data = data.get("user_profile", {})

        try:
            with transaction.atomic():
                self.update_user_profile(instance.userprofile, user_profile_data)
                self.update_user(instance, user_data, partial)

                AuditHistory.objects.create(
                    user=request.user, action=f"Updated user: {original_username}"
                )

                return Response(self.get_serializer(instance).data)
        except (Group.DoesNotExist, DataGroup.DoesNotExist) as e:
            raise ValidationError({"detail": str(e)})

    def perform_destroy(self, instance):
        username = instance.username

        AuditHistory.objects.create(
            user=self.request.user, action=f"Deleted user: {username}"
        )

        instance.delete()

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

    @action(detail=True, methods=["post"], url_path="assign-shift")
    def assign_shift(self, request, pk=None):
        """
        API endpoint to assign a shift to the userpos.
        """
        user = get_object_or_404(User, pk=pk)
        shift = request.data.get("shift")

        if not shift:
            return Response(
                {"error": "Shift is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not hasattr(user, "userprofile"):
            return Response(
                {"error": "User profile does not exist for the assigned user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.userprofile.shift = shift
        user.userprofile.save()

        AuditHistory.objects.create(
            user=request.user,
            action=f"Assigned shift '{shift}' to user: {user.username}",
        )

        return Response(
            {"message": f"Shift '{shift}' assigned successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="inspection_points_pins_data")
    def get_inspection_points_pins_data(self, request):
        """Fetches inspection points and sorts them based on user's location."""
        today = now().date()

        user_location = get_user_location(request)
        if isinstance(user_location, Response):
            return user_location
        evinces = self.get_evinces_for_user(request.user, today)
        if isinstance(evinces, Response):
            return evinces
        inspection_data = sort_evinces_by_distance(evinces, user_location)

        return Response(
            {"inspections_points_pins_data": inspection_data},
            status=status.HTTP_200_OK,
        )

    def get_evinces_for_user(self, user, today):
        """Fetches evinces based on the user's role."""
        if not hasattr(user, "userprofile") or not user.userprofile:
            return Response(
                {"error": "User profile or role not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = user.userprofile.role.name

        if role == "Admin":
            inspector_id = self.request.query_params.get("inspector")
            if not inspector_id:
                return Response(
                    {"error": "Inspector ID is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = User.objects.get(id=inspector_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "Inspector not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Evince.objects.filter(assigned_to=user, start_date_time__date=today)

        elif role == "Manager":
            return Evince.objects.filter(reviewed_by=user, start_date_time__date=today)

        elif role == "Inspector":
            return Evince.objects.filter(assigned_to=user, start_date_time__date=today)

        return Response(
            {"error": "Unauthorized role."},
            status=status.HTTP_403_FORBIDDEN,
        )
