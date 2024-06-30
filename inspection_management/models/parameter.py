from django.db import models

from inspection_management.models import InspectionAnalysis, Unit
from users.models.user import User

from .datagroup import DataGroup


class Parameter(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=255)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    inspection_analysis = models.ForeignKey(
        InspectionAnalysis, on_delete=models.CASCADE
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    avg_value = models.IntegerField(null=True, blank=True)
    string_value = models.CharField(max_length=255, null=True, blank=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
