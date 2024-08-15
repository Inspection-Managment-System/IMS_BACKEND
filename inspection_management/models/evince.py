from django.db import models

from inspection_management.models import (BusinessUnit, InspectionAnalysis,
                                          InspectionPoint)
from users.models.user import User


class Evince(models.Model):
    STATUS_CHOICES = [
        ("Logged", "Logged"),
        ("ResultsEntered", "ResultsEntered"),
        ("Completed", "Completed"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Reassigned", "Reassigned"),
    ]
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    description = models.CharField(max_length=255)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
    )
    inspection_point = models.ForeignKey(InspectionPoint, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_inspector",
        null=True,
        blank=True,
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_reviewer"
    )
    inspection_analyses = models.ManyToManyField(InspectionAnalysis)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Logged")
    crtical_instructions_file_name = models.CharField(
        max_length=255, blank=True, null=True
    )
    crtical_instructions = models.TextField(blank=True, null=True)
    start_date_time = models.DateTimeField(blank=True, null=True)
    end_date_time = models.DateTimeField(blank=True, null=True)
    reassigned = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = f"{self.inspection_point.business_unit.name}_{self.inspection_point.name}_{self.pk}"
        super().save(*args, **kwargs)
