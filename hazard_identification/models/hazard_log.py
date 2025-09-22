from django.db import models
from django.conf import settings
from django.utils import timezone
from inspection_management.models import BusinessUnit, Location, ExternalDepartment


class HazardIdentification(models.Model):
    """Main model for hazard identification log entries"""
    
    STATUS_CHOICES = [
        ('Logged', 'Logged'),
        ('InspectorReview', 'Inspector Review'),
        ('ManagerAssignment', 'Manager Assignment'),
        ('InProgress', 'In Progress'),
        ('Done', 'Done'),
    ]
    
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    
    # Basic Information
    serial_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Auto-generated serial number for tracking"
    )
    hazard_description = models.TextField(
        help_text="Detailed description of the identified hazard"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='hazards',
        help_text="Specific location where the hazard was found"
    )
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name='hazards',
        help_text="Business unit where the hazard was identified"
    )
    
    # Classification
    category = models.ForeignKey(
        'HazardCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hazards'
    )
    severity_level = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='Medium',
        help_text="Severity level of the hazard"
    )
    priority_level = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Medium',
        help_text="Priority level for addressing the hazard"
    )
    
    # Assessment and Controls
    recommended_controls = models.TextField(
        help_text="Recommended controls or actions to address the hazard"
    )
    estimated_resolution_time = models.PositiveIntegerField(
        default=7,
        help_text="Estimated time in days to resolve the hazard"
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="Any additional notes or observations"
    )
    
    # Workflow Management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Logged',
        help_text="Current status of the hazard"
    )
    
    # User Assignments
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_hazards',
        help_text="User who identified and logged the hazard"
    )
    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_hazards',
        help_text="Manager responsible for overseeing this hazard"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_hazards',
        help_text="Inspector assigned to address the hazard"
    )
    assigned_department = models.ForeignKey(
        ExternalDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_hazards',
        help_text="Department assigned to address the hazard"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_hazards',
        help_text="Manager who reviewed and assigned the hazard"
    )
    
    # Dates and Tracking
    reported_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when the hazard was first reported"
    )
    target_completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Target date for completing the hazard resolution"
    )
    actual_completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual date when the hazard was resolved"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last time the hazard record was updated"
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Hazard Identification"
        verbose_name_plural = "Hazard Identifications"
        ordering = ['-reported_date']
    
    def __str__(self):
        return f"Hazard #{self.serial_number}: {self.hazard_description[:50]}"
    
    def save(self, *args, **kwargs):
        # Auto-generate serial number if not provided
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)
    
    def generate_serial_number(self):
        """Generate a unique serial number for the hazard"""
        from datetime import datetime
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        
        # Count existing hazards for this month/year
        count = HazardIdentification.objects.filter(
            reported_date__year=year,
            reported_date__month=month
        ).count() + 1
        
        return f"HAZ-{year}{month:02d}-{count:04d}"
    
    @property
    def is_overdue(self):
        """Check if the hazard is overdue"""
        if self.target_completion_date and self.status != 'Done':
            return timezone.now() > self.target_completion_date
        return False
    
    @property
    def days_overdue(self):
        """Calculate how many days the hazard is overdue"""
        if self.is_overdue:
            return (timezone.now() - self.target_completion_date).days
        return 0
    
    @property
    def status_color(self):
        """Get color code for status display"""
        color_map = {
            'Logged': '#dc2626',      # Red
            'InspectorReview': '#ea580c',  # Orange
            'ManagerAssignment': '#d97706',  # Yellow
            'InProgress': '#2563eb',   # Blue
            'Done': '#16a34a',        # Green
        }
        return color_map.get(self.status, '#6b7280')
