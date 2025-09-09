from django.db import models
from django.utils import timezone
from users.models.user import User
from .evince import Evince


class MaintenanceResult(models.Model):
    """Maintenance-specific result entry for maintenance inspections"""
    
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Predictive'),
        ('emergency', 'Emergency'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    EQUIPMENT_CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    DOWNTIME_IMPACT_CHOICES = [
        ('none', 'No Downtime'),
        ('minimal', 'Minimal Impact'),
        ('moderate', 'Moderate Impact'),
        ('significant', 'Significant Impact'),
        ('critical', 'Critical Impact'),
    ]
    
    evince = models.ForeignKey(Evince, on_delete=models.CASCADE, related_name='maintenance_results')
    entered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_results_entered', null=True, blank=True)
    entered_at = models.DateTimeField(default=timezone.now)
    
    # Maintenance Assessment Results
    maintenance_type = models.CharField(
        max_length=20, 
        choices=MAINTENANCE_TYPE_CHOICES, 
        blank=True, 
        null=True,
        help_text="Type of maintenance performed"
    )
    maintenance_priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        blank=True, 
        null=True,
        help_text="Priority level of maintenance"
    )
    equipment_condition_before = models.CharField(
        max_length=20, 
        choices=EQUIPMENT_CONDITION_CHOICES, 
        blank=True, 
        null=True,
        help_text="Equipment condition before maintenance"
    )
    equipment_condition_after = models.CharField(
        max_length=20, 
        choices=EQUIPMENT_CONDITION_CHOICES, 
        blank=True, 
        null=True,
        help_text="Equipment condition after maintenance"
    )
    maintenance_actions_taken = models.TextField(
        blank=True, 
        null=True,
        help_text="Detailed description of maintenance actions performed"
    )
    parts_replaced = models.TextField(
        blank=True, 
        null=True,
        help_text="List of parts replaced during maintenance"
    )
    parts_required = models.TextField(
        blank=True, 
        null=True,
        help_text="List of parts required but not available"
    )
    
    # Maintenance Execution
    maintenance_start_time = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="When maintenance work started"
    )
    maintenance_end_time = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="When maintenance work completed"
    )
    downtime_duration = models.DurationField(
        blank=True, 
        null=True,
        help_text="Total downtime duration"
    )
    downtime_impact = models.CharField(
        max_length=20, 
        choices=DOWNTIME_IMPACT_CHOICES, 
        blank=True, 
        null=True,
        help_text="Impact of downtime on operations"
    )
    maintenance_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Total cost of maintenance"
    )
    
    # Safety & Quality
    safety_checks_performed = models.BooleanField(
        default=False,
        help_text="Whether safety checks were performed"
    )
    safety_issues_identified = models.TextField(
        blank=True, 
        null=True,
        help_text="Any safety issues identified during maintenance"
    )
    quality_checks_performed = models.BooleanField(
        default=False,
        help_text="Whether quality checks were performed"
    )
    quality_issues_identified = models.TextField(
        blank=True, 
        null=True,
        help_text="Any quality issues identified during maintenance"
    )
    
    # Follow-up & Documentation
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether follow-up maintenance is required"
    )
    follow_up_date = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Date for follow-up maintenance"
    )
    next_maintenance_due = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Date for next scheduled maintenance"
    )
    documentation_updated = models.BooleanField(
        default=False,
        help_text="Whether maintenance documentation was updated"
    )
    training_required = models.BooleanField(
        default=False,
        help_text="Whether additional training is required"
    )
    
    # Additional Notes
    additional_notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes or observations"
    )
    
    # Technical Measurements (same as regular inspection)
    inspection_analyses = models.ManyToManyField(
        'InspectionAnalysis', 
        blank=True,
        help_text="Analysis types used for technical measurements"
    )
    parameter_results = models.JSONField(
        blank=True, 
        null=True,
        help_text="Parameter measurement results in format: {'parameter_id': 'value'}"
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
        return f"Maintenance Result for {self.evince.name} - {self.entered_by.username}"
