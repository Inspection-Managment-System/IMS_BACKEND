from django.db import models
from users.models.user import User
from .datagroup import DataGroup


class RiskLevel(models.Model):
    """Configurable Risk Levels for HSE Risk Assessments"""
    name = models.CharField(max_length=100)  # Display name: "Low", "Medium", etc.
    value = models.CharField(max_length=50, unique=True)  # Backend value: "low", "medium"
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

