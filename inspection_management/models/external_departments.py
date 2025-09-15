from django.db import models
from django.utils import timezone
from users.models import User


class ExternalDepartment(models.Model):
    """Model for external departments (LIMS, LW8, etc.) that can be assigned mitigation work"""
    
    DEPARTMENT_TYPES = [
        ('LIMS', 'Laboratory Information Management System'),
        ('LW8', 'LW8 Process System'),
        ('MAINTENANCE', 'Maintenance Department'),
        ('SAFETY', 'Safety Department'),
        ('ENVIRONMENTAL', 'Environmental Department'),
        ('QUALITY', 'Quality Control'),
        ('OTHER', 'Other External System'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]
    
    name = models.CharField(max_length=200, help_text="Department name")
    department_type = models.CharField(max_length=50, choices=DEPARTMENT_TYPES, help_text="Type of external system")
    description = models.TextField(blank=True, null=True, help_text="Department description")
    
    # External system connection details
    external_system_url = models.URLField(blank=True, null=True, help_text="External system API endpoint")
    external_system_id = models.CharField(max_length=100, blank=True, null=True, help_text="Department ID in external system")
    api_key = models.CharField(max_length=500, blank=True, null=True, help_text="API key for external system")
    
    # Contact information
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Capabilities
    capabilities = models.JSONField(default=list, blank=True, help_text="List of department capabilities")
    specializations = models.JSONField(default=list, blank=True, help_text="List of specializations")
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    is_available = models.BooleanField(default=True, help_text="Whether department is available for assignments")
    max_concurrent_assignments = models.IntegerField(default=5, help_text="Maximum concurrent assignments")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_external_departments')
    
    class Meta:
        db_table = 'external_departments'
        verbose_name = 'External Department'
        verbose_name_plural = 'External Departments'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_department_type_display()})"
    
    @property
    def current_assignments_count(self):
        """Get current number of active assignments"""
        from .external_departments import ExternalDepartmentAssignment
        return ExternalDepartmentAssignment.objects.filter(
            external_department=self,
            status__in=['ASSIGNED', 'IN_PROGRESS', 'COMPLETED']
        ).count()
    
    @property
    def is_available_for_assignment(self):
        """Check if department can accept new assignments"""
        return (
            self.is_available and 
            self.status == 'ACTIVE' and 
            self.current_assignments_count < self.max_concurrent_assignments
        )


class ExternalDepartmentAssignment(models.Model):
    """Track assignments to external departments"""
    
    evince = models.ForeignKey('Evince', on_delete=models.CASCADE, related_name='external_assignments')
    external_department = models.ForeignKey(ExternalDepartment, on_delete=models.CASCADE, related_name='assignments')
    
    # Assignment details
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='external_assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    target_completion_date = models.DateTimeField()
    
    # External system tracking
    external_task_id = models.CharField(max_length=100, blank=True, null=True, help_text="Task ID in external system")
    external_status = models.CharField(max_length=50, blank=True, null=True, help_text="Status in external system")
    last_sync_at = models.DateTimeField(blank=True, null=True, help_text="Last sync with external system")
    
    # Assignment status
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    
    # Communication
    notes = models.TextField(blank=True, null=True)
    external_response = models.JSONField(default=dict, blank=True, help_text="Response from external system")
    
    # Mitigation completion details (for HSE Risk Assessment workflow)
    completion_notes = models.TextField(blank=True, null=True, help_text="Notes from external department upon completion")
    mitigation_actions = models.TextField(blank=True, null=True, help_text="Detailed mitigation actions performed by external department")
    evidence_data = models.JSONField(default=dict, blank=True, help_text="Evidence data (file paths, links, etc.)")
    cost_incurred = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cost incurred by external department for mitigation")
    
    class Meta:
        db_table = 'external_department_assignments'
        verbose_name = 'External Department Assignment'
        verbose_name_plural = 'External Department Assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.evince.name} -> {self.external_department.name}"
 