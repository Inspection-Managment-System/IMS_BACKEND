from django.db import models
from django.utils import timezone
from users.models.user import User
from .evince import Evince


class HSEResult(models.Model):
    """HSE-specific result entry for HSE observations"""
    
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    MITIGATION_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('partially_complete', 'Partially Complete'),
    ]
    
    FOLLOW_UP_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]
    
    MITIGATION_EFFECTIVENESS_CHOICES = [
        ('effective', 'Effective'),
        ('partially_effective', 'Partially Effective'),
        ('not_effective', 'Not Effective'),
    ]
    
    COMPLIANCE_STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('under_review', 'Under Review'),
    ]
    
    evince = models.ForeignKey(Evince, on_delete=models.CASCADE, related_name='hse_results')
    entered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hse_results_entered', null=True, blank=True)
    entered_at = models.DateTimeField(default=timezone.now)
    
    # Risk Assessment Results
    risk_level_after_assessment = models.CharField(
        max_length=20, 
        choices=RISK_LEVEL_CHOICES, 
        blank=True, 
        null=True,
        help_text="Risk level after assessment"
    )
    risk_mitigation_status = models.CharField(
        max_length=20, 
        choices=MITIGATION_STATUS_CHOICES, 
        blank=True, 
        null=True,
        help_text="Status of risk mitigation"
    )
    immediate_actions_taken = models.TextField(
        blank=True, 
        null=True,
        help_text="Immediate safety measures taken"
    )
    root_cause_analysis = models.TextField(
        blank=True, 
        null=True,
        help_text="Identified root causes"
    )
    preventive_measures = models.TextField(
        blank=True, 
        null=True,
        help_text="Preventive actions implemented"
    )
    
    # Mitigation & Follow-up
    mitigation_actions_implemented = models.TextField(
        blank=True, 
        null=True,
        help_text="Description of mitigation actions taken"
    )
    mitigation_completion_date = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Date when mitigation was completed"
    )
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether follow-up is required"
    )
    follow_up_date = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Date for follow-up inspection"
    )
    follow_up_status = models.CharField(
        max_length=20, 
        choices=FOLLOW_UP_STATUS_CHOICES, 
        blank=True, 
        null=True,
        help_text="Status of follow-up"
    )
    mitigation_effectiveness = models.CharField(
        max_length=20, 
        choices=MITIGATION_EFFECTIVENESS_CHOICES, 
        blank=True, 
        null=True,
        help_text="Effectiveness of mitigation actions"
    )
    
    # Safety & Compliance
    safety_measures_applied = models.TextField(
        blank=True, 
        null=True,
        help_text="Safety protocols implemented"
    )
    regulatory_compliance_status = models.CharField(
        max_length=20, 
        choices=COMPLIANCE_STATUS_CHOICES, 
        blank=True, 
        null=True,
        help_text="Regulatory compliance status"
    )
    documentation_updated = models.BooleanField(
        default=False,
        help_text="Whether documentation was updated"
    )
    training_required = models.BooleanField(
        default=False,
        help_text="Whether training is required"
    )
    training_completed = models.BooleanField(
        default=False,
        help_text="Whether training was completed"
    )
    
    # Additional Notes
    additional_notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes or observations"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20, 
        choices=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='draft'
    )
    
    class Meta:
        ordering = ['-entered_at']
        unique_together = ['evince', 'entered_by']
    
    def __str__(self):
        return f"HSE Result for {self.evince.name} - {self.entered_by.username}"
