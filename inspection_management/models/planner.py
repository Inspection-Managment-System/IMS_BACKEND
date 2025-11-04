from django.db import models

from inspection_management.models import (BusinessUnit, InspectionAnalysis,
                                          InspectionPoint, Parameter)
from users.models.user import User


class Planner(models.Model):
    RULE_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
    ]
    name = models.CharField(max_length=255, default="Planner", unique=True)
    rule = models.CharField(max_length=10, choices=RULE_CHOICES, null=True, blank=True)
    evince_description = models.CharField(
        max_length=255, default="", null=True, blank=True
    )
    evince_business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
    )
    evince_inspection_point = models.ForeignKey(
        InspectionPoint,
        on_delete=models.CASCADE,
    )
    evince_inspection_analyses = models.ManyToManyField(InspectionAnalysis)
    evince_parameters = models.ManyToManyField(
        Parameter, 
        blank=True,
        help_text="Specific parameters to include when creating inspections"
    )

    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_planner_reviewer",
        null=True,
        blank=True,
    )
    evince_assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_planner_inspector",
        null=True,
        blank=True,
        help_text="User assigned to perform the inspection when created by planner"
    )
    day_of_week = models.CharField(max_length=255, blank=True, null=True)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    month = models.CharField(max_length=255, blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)
