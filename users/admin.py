from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models.user import User
from .models.userprofile import UserProfile

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
