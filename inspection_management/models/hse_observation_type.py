from django.db import models
from users.models.user import User
from .datagroup import DataGroup


class HSEObservationType(models.Model):
    """Configurable HSE Observation Types"""
    name = models.CharField(max_length=100)  # Display name: "Slip/Trip Hazard", etc.
    value = models.CharField(max_length=50, unique=True)  # Backend value: "slip_trip"
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)  # For sorting in dropdowns
    group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['value', 'group']
    
    def __str__(self):
        return f"{self.name} ({self.group.name})"

