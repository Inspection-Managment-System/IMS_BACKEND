from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models

from inspection_management.models import DataGroup


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    role = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    data_group = models.ForeignKey(
        DataGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_profiles",
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", default="static/images/avatars/1.png"
    )
