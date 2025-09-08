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

    EVINCE_TYPE_CHOICES = [
        ("inspection", "Regular Inspection"),
        ("hse_observation", "HSE Observation"),
        ("maintenance", "Maintenance Check"),
        ("compliance", "Compliance Audit"),
    ]
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    evince_type = models.CharField(max_length=20, choices=EVINCE_TYPE_CHOICES, default="inspection")
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
    )
    inspection_point = models.ForeignKey(InspectionPoint, on_delete=models.CASCADE)
    logged_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="logged_by",
        null=True,
        blank=True,
    )
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

    # HSE-specific fields (only used when evince_type = 'hse_observation')
    hse_observation_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of HSE observation")
    hse_risk_level = models.CharField(max_length=20, blank=True, null=True, help_text="Risk level for HSE observation")
    hse_risk_category = models.CharField(max_length=20, blank=True, null=True, help_text="Risk category for HSE observation")
    hse_mitigation_required = models.CharField(max_length=10, blank=True, null=True, help_text="Required mitigation actions (Yes/No)")
    hse_follow_up_required = models.BooleanField(default=False, help_text="Whether follow-up is required")
    hse_follow_up_date = models.DateTimeField(blank=True, null=True, help_text="Date for follow-up")

    # Maintenance-specific fields (only used when evince_type = 'maintenance')
    maintenance_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of maintenance")
    maintenance_priority = models.CharField(max_length=20, blank=True, null=True, help_text="Priority level for maintenance")
    maintenance_status = models.CharField(max_length=20, blank=True, null=True, help_text="Status of maintenance")
    maintenance_equipment = models.CharField(max_length=255, blank=True, null=True, help_text="Equipment or asset being maintained")
    maintenance_description = models.TextField(blank=True, null=True, help_text="Description of maintenance work")
    maintenance_parts_required = models.BooleanField(default=False, help_text="Whether parts are required")
    maintenance_safety_check = models.BooleanField(default=False, help_text="Whether safety check is required")

    # Compliance-specific fields (only used when evince_type = 'compliance')
    compliance_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of compliance audit")
    compliance_standard = models.CharField(max_length=50, blank=True, null=True, help_text="Standard or regulation being audited")
    compliance_priority = models.CharField(max_length=20, blank=True, null=True, help_text="Priority level for compliance audit")
    compliance_auditor = models.CharField(max_length=255, blank=True, null=True, help_text="Auditor or inspector name")
    compliance_scope = models.TextField(blank=True, null=True, help_text="Scope of the compliance audit")
    compliance_documentation_required = models.BooleanField(default=False, help_text="Whether documentation is required")
    compliance_corrective_action = models.BooleanField(default=False, help_text="Whether corrective action is required")

    @classmethod
    def get_status_labels(cls):
        return dict(cls.STATUS_CHOICES)

    @classmethod
    def get_evince_type_labels(cls):
        return dict(cls.EVINCE_TYPE_CHOICES)

    @classmethod
    def get_evinces_count_with_status(cls, status):
        return cls.objects.filter(status=status).count()

    @classmethod
    def get_evinces_count_with_type(cls, evince_type):
        return cls.objects.filter(evince_type=evince_type).count()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = f"{self.inspection_point.business_unit.name}_{self.inspection_point.name}_{self.pk}"
        super().save(*args, **kwargs)
