from django.db import models

from inspection_management.models import (BusinessUnit, InspectionAnalysis,
                                          InspectionPoint)
from users.models.user import User


class Planner(models.Model):
    RULE_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
    ]
    name = models.CharField(max_length=100, default="Planner", unique=True)
    rule = models.CharField(max_length=10, choices=RULE_CHOICES, null=True, blank=True)
    evince_description = models.CharField(max_length=255, default="")
    evince_business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
    )
    evince_inspection_point = models.ForeignKey(
        InspectionPoint,
        on_delete=models.CASCADE,
    )
    evince_inspection_analyses = models.ManyToManyField(InspectionAnalysis)

    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=255, blank=True, null=True)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    month = models.CharField(max_length=255, blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)
