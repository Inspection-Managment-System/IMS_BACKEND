from django.db import models
from django.utils import timezone
from users.models.user import User
from .business_unit import BusinessUnit


class HSEObservation(models.Model):
    """HSE Observation with workflow states"""
    RISK_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ]
    
    WORKFLOW_STATES = [
        ('DRAFT', 'Draft'),
        ('PENDING_VALIDATION', 'Pending Validation'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('EVIDENCE_SUBMITTED', 'Evidence Submitted'),
        ('CLOSED', 'Closed')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    risk_category = models.CharField(max_length=50, default='Safety')
    affected_department = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    workflow_state = models.CharField(max_length=50, choices=WORKFLOW_STATES, default='DRAFT')
    target_date = models.DateTimeField(null=True, blank=True)
    
    # User assignments
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hse_observations_created')
    validated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hse_observations_validated', null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hse_observations_assigned', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hse_observation'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"HSE Observation: {self.title}"


class HSEWorkflowHistory(models.Model):
    """HSE Workflow history tracking"""
    observation = models.ForeignKey(HSEObservation, on_delete=models.CASCADE, related_name='workflow_history')
    from_state = models.CharField(max_length=50)
    to_state = models.CharField(max_length=50)
    action_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hse_workflow_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.observation.title} - {self.from_state} to {self.to_state}"


class HSEEvidence(models.Model):
    """HSE Evidence for observations"""
    observation = models.ForeignKey(HSEObservation, on_delete=models.CASCADE, related_name='evidence')
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=200)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hse_evidence'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Evidence for {self.observation.title}"
