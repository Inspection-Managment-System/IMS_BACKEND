from django.db import models
from inspection_management.models import BusinessUnit, InspectionAnalysis, InspectionPoint, Parameter
from users.models.user import User


class HSEPlanner(models.Model):
    """Planner for HSE Risk Assessments - supports both observation and parameter based"""
    
    RULE_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
    ]
    
    ASSESSMENT_TYPE_CHOICES = [
        ("observation", "Observation Based"),
        ("parameter", "Parameter Based"),
    ]
    
    # Basic fields
    name = models.CharField(max_length=255, default="HSE Planner", unique=True)
    rule = models.CharField(max_length=10, choices=RULE_CHOICES, null=True, blank=True)
    assessment_type = models.CharField(
        max_length=20, 
        choices=ASSESSMENT_TYPE_CHOICES, 
        default="parameter",
        help_text="Type of HSE risk assessment"
    )
    
    # Evince creation fields
    evince_description = models.CharField(max_length=255, default="", null=True, blank=True)
    evince_business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    evince_inspection_point = models.ForeignKey(InspectionPoint, on_delete=models.CASCADE)
    
    # For parameter-based assessments
    evince_inspection_analyses = models.ManyToManyField(InspectionAnalysis, blank=True)
    evince_parameters = models.ManyToManyField(
        Parameter, 
        blank=True,
        help_text="Specific parameters for parameter-based assessments"
    )
    
    # For observation-based assessments
    hse_observation_details = models.TextField(
        blank=True, 
        null=True,
        help_text="Observation details for observation-based assessments"
    )
    
    # User assignments
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hse_planner_created")
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hse_planner_reviewer",
        null=True,
        blank=True,
        help_text="Manager who will review created assessments"
    )
    evince_assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hse_planner_inspector",
        null=True,
        blank=True,
        help_text="Inspector assigned to perform the assessment"
    )
    
    # Schedule fields
    day_of_week = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated days for Weekly rule")
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    month = models.CharField(max_length=255, blank=True, null=True, help_text="For Monthly rule")
    
    # Attachments
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'hse_planner'
        ordering = ['-changed_on']
    
    def __str__(self):
        return f"{self.name} - {self.get_rule_display()} - {self.get_assessment_type_display()}"

