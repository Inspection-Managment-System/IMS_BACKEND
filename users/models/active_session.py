"""
Active Session Model - Track Concurrent User Logins
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class ActiveSession(models.Model):
    """
    Track active user sessions for license enforcement
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='active_sessions'
    )
    session_token = models.CharField(max_length=500, unique=True)
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'active_sessions'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    
    @classmethod
    def get_active_session_count(cls):
        """
        Get count of currently active sessions
        Excludes sessions older than 24 hours
        """
        cutoff_time = timezone.now() - timedelta(hours=24)
        return cls.objects.filter(
            is_active=True,
            last_activity__gte=cutoff_time
        ).count()
    
    @classmethod
    def cleanup_old_sessions(cls):
        """
        Remove sessions older than 24 hours
        """
        cutoff_time = timezone.now() - timedelta(hours=24)
        old_sessions = cls.objects.filter(last_activity__lt=cutoff_time)
        count = old_sessions.count()
        old_sessions.delete()
        return count
    
    @classmethod
    def get_user_session_count(cls, user):
        """
        Get active session count for specific user
        """
        cutoff_time = timezone.now() - timedelta(hours=24)
        return cls.objects.filter(
            user=user,
            is_active=True,
            last_activity__gte=cutoff_time
        ).count()
    
    @classmethod
    def end_user_sessions(cls, user):
        """
        End all active sessions for a user
        """
        cls.objects.filter(user=user, is_active=True).update(is_active=False)

