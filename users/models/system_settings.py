from django.db import models


class SystemSettings(models.Model):
    """Track system setup status and configuration"""
    
    setup_completed = models.BooleanField(default=False)
    setup_completed_at = models.DateTimeField(null=True, blank=True)
    app_version = models.CharField(max_length=50, default="1.0.0")
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"System Settings (Setup: {self.setup_completed})"
    
    @classmethod
    def is_setup_completed(cls):
        """Check if system setup is completed"""
        settings = cls.objects.first()
        return settings.setup_completed if settings else False
    
    @classmethod
    def mark_setup_completed(cls):
        """Mark setup as completed"""
        from django.utils import timezone
        settings, created = cls.objects.get_or_create(id=1)
        settings.setup_completed = True
        settings.setup_completed_at = timezone.now()
        settings.save()
        return settings

