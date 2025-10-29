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
        # HSE Risk Management specific statuses
        ("InspectorReview", "Inspector Review"),
        ("RiskValidated", "Risk Validated"),
        ("ManagerAssignment", "Manager Assignment"),
        ("MitigationInProgress", "Mitigation In Progress"),
        ("MitigationCompleted", "Mitigation Completed"),
        ("LIMSInProgress", "LIMS In Progress"),
        ("LIMSCompleted", "LIMS Completed"),
        ("ManagerApproval", "Manager Approval"),
    ]

    EVINCE_TYPE_CHOICES = [
        ("inspection", "Regular Inspection"),
        ("hse_observation", "HSE Observation"),
        ("maintenance", "Maintenance Check"),
        ("compliance", "Compliance Audit"),
        ("hse_risk_management", "HSE Risk Management"),
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

    # HSE Risk Management specific fields (only used when evince_type = 'hse_risk_management')
    hse_risk_assessment = models.JSONField(default=dict, blank=True, help_text="Inspector's risk assessment data")
    hse_risk_notes = models.TextField(blank=True, null=True, help_text="Risk assessment notes from inspector")
    hse_risk_level = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical'), ('No Risk Validated', 'No Risk Validated')
    ], help_text="Risk level assessment")
    hse_risk_category = models.CharField(max_length=50, blank=True, null=True, help_text="Risk category")
    hse_inspection_date = models.DateTimeField(blank=True, null=True, help_text="Date of inspection")
    hse_lims_reference_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reference ID from LIMS system")
    hse_lims_status = models.CharField(max_length=50, blank=True, null=True, help_text="Status from LIMS system")
    hse_investigation_details = models.TextField(blank=True, null=True, help_text="Investigation details from LIMS")
    hse_mitigation_actions = models.TextField(blank=True, null=True, help_text="Mitigation actions taken")
    hse_approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hse_risk_approved", null=True, blank=True, help_text="Manager who approved the investigation")
    hse_approved_at = models.DateTimeField(blank=True, null=True, help_text="Date of approval")
    hse_manager_decision_final = models.BooleanField(default=False, help_text="Whether manager has made final decision (approve/reject) - prevents external sync from overwriting")
    
    # Additional HSE Risk Workflow fields
    hse_risk_valid = models.BooleanField(default=False, help_text="Whether risk assessment is valid")
    hse_out_of_spec_results = models.JSONField(default=list, blank=True, help_text="List of out-of-spec parameter results")
    hse_observation_details = models.TextField(blank=True, null=True, help_text="Inspector's observation details")
    hse_mitigation_department = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, related_name="hse_mitigation_assignments", null=True, blank=True, help_text="Department assigned for mitigation")
    hse_mitigation_assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hse_mitigation_assignments", null=True, blank=True, help_text="User assigned for mitigation work")
    hse_mitigation_target_date = models.DateTimeField(blank=True, null=True, help_text="Target date for mitigation completion")
    hse_mitigation_evidence = models.TextField(blank=True, null=True, help_text="Evidence submitted by mitigation department")
    hse_mitigation_work_done = models.TextField(blank=True, null=True, help_text="Actual mitigation work performed by mitigation user (separate from manager's instructions)")
    hse_mitigation_completed = models.BooleanField(default=False, help_text="Whether mitigation work is completed")
    hse_risk_closed = models.BooleanField(default=False, help_text="Whether risk observation is closed")
    hse_risk_rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for risk rejection if not valid")
    
    # HSE Risk Trigger Type (new field for observation-only vs parameter-based)
    hse_risk_trigger_type = models.CharField(
        max_length=25, 
        blank=True, 
        null=True,
        choices=[
            ('AUTO_OUT_OF_SPEC', 'Automatic - Out of Spec Parameters'),
            ('MANUAL_OBSERVATION', 'Manual - Observation Only'),
        ],
        help_text="How this HSE risk assessment was triggered (automatic from parameters or manual observation)"
    )
    hse_has_parameters = models.BooleanField(
        default=True,
        help_text="Whether this HSE risk assessment has associated parameter measurements"
    )

    @classmethod
    def get_status_labels(cls):
        return dict(cls.STATUS_CHOICES)
    
    @classmethod
    def get_status_labels_by_type(cls, evince_type=None):
        """Get status labels filtered by evince type"""
        all_statuses = dict(cls.STATUS_CHOICES)
        
        if evince_type == 'inspection':
            # Only return regular inspection statuses
            regular_statuses = [
                "Logged", "ResultsEntered", "Completed", 
                "Approved", "Rejected", "Reassigned"
            ]
            return {k: v for k, v in all_statuses.items() if k in regular_statuses}
        elif evince_type == 'hse_risk_management':
            # Only return HSE Risk Management statuses
            hse_statuses = [
                "InspectorReview", "RiskValidated", "ManagerAssignment",
                "LIMSInProgress", "LIMSCompleted", "ManagerApproval", "Completed",
                "Rejected", "Reassigned"
            ]
            return {k: v for k, v in all_statuses.items() if k in hse_statuses}
        else:
            # Return all statuses if no type specified
            return all_statuses

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
        # Generate unique name after saving to get the pk
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and (not self.name or self.name.endswith('_None')):
            # Generate unique name with timestamp to avoid conflicts
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            self.name = f"{self.inspection_point.business_unit.name}_{self.inspection_point.name}_{self.pk}_{timestamp}"
            # Update name directly in database to avoid another save call
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE inspection_management_evince SET name = %s WHERE id = %s",
                    [self.name, self.pk]
                )

    # Department assignment field
    assigned_department = models.CharField(max_length=200, blank=True, null=True, help_text="Department assigned for mitigation work")


class HSERiskAssessmentResult(models.Model):
    """
    Model to store HSE Risk Assessment parameter results and risk assessment data
    """
    evince = models.ForeignKey(Evince, on_delete=models.CASCADE, related_name='hse_risk_assessment_results')
    
    # Parameter details
    parameter_name = models.CharField(max_length=255)
    parameter_value = models.TextField(null=True, blank=True)
    parameter_comments = models.TextField(null=True, blank=True)
    parameter_status = models.CharField(
        max_length=20,
        choices=[
            ('Incomplete', 'Incomplete'),
            ('Completed', 'Completed'),
        ],
        default='Incomplete'
    )
    
    # Risk Assessment details
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
            ('CRITICAL', 'Critical'),
        ],
        null=True,
        blank=True
    )
    
    risk_category = models.CharField(
        max_length=50,
        choices=[
            ('Equipment', 'Equipment'),
            ('Safety', 'Safety'),
            ('Environmental', 'Environmental'),
            ('Process', 'Process'),
        ],
        null=True,
        blank=True
    )
    
    risk_notes = models.TextField(null=True, blank=True)
    observation_details = models.TextField(null=True, blank=True)
    risk_valid = models.BooleanField(null=True, blank=True)
    
    # Mitigation details
    mitigation_actions = models.TextField(null=True, blank=True)
    mitigation_target_date = models.DateField(null=True, blank=True)
    mitigation_evidence = models.TextField(null=True, blank=True)
    mitigation_completed = models.BooleanField(default=False)
    risk_closed = models.BooleanField(default=False)
    
    # Audit fields
    created_on = models.DateTimeField(auto_now_add=True)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'inspection_management_hseriskassessmentresult'
        verbose_name = 'HSE Risk Assessment Result'
        verbose_name_plural = 'HSE Risk Assessment Results'
        ordering = ['-created_on']
    
    def __str__(self):
        return f"HSE Risk Assessment {self.evince.id} - {self.parameter_name}"
