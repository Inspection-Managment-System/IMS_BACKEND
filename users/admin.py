from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models.audit_history import AuditHistory
from .models.notification import Notification
from .models.user import User
from .models.userprofile import UserProfile

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(AuditHistory)
admin.site.register(Notification)
