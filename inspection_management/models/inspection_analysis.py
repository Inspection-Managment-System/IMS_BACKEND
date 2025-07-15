from django.db import models

from inspection_management.models import AnalysisType, Equipment, Location
from users.models.user import User

from .datagroup import DataGroup


class InspectionAnalysis(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, null=True, blank=True
    )
    analysis_type = models.ForeignKey(AnalysisType, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    reported_name = models.CharField(max_length=50)
    alias_name = models.CharField(max_length=50)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
