from django.db import models
from django.utils import timezone
from users.models.user import User
from .inspection_point import InspectionPoint
from .business_unit import BusinessUnit


class HSEEnvironmentalData(models.Model):
    """HSE Environmental monitoring data"""
    inspection_point = models.ForeignKey(InspectionPoint, on_delete=models.CASCADE, related_name='hse_environmental_data')
    timestamp = models.DateTimeField(default=timezone.now)
    air_quality_pm25 = models.FloatField(null=True, blank=True)
    air_quality_pm10 = models.FloatField(null=True, blank=True)
    air_quality_vocs = models.FloatField(null=True, blank=True)
    air_quality_nox = models.FloatField(null=True, blank=True)
    air_quality_sox = models.FloatField(null=True, blank=True)
    water_quality_ph = models.FloatField(null=True, blank=True)
    water_quality_temperature = models.FloatField(null=True, blank=True)
    water_quality_dissolved_oxygen = models.FloatField(null=True, blank=True)
    emissions_co2 = models.FloatField(null=True, blank=True)
    emissions_ch4 = models.FloatField(null=True, blank=True)
    waste_generation = models.FloatField(null=True, blank=True)
    waste_disposal = models.FloatField(null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.inspection_point.name} - {self.timestamp}"


class HSESafetyIncident(models.Model):
    """HSE Safety incident tracking"""
    INCIDENT_TYPES = [
        ('near_miss', 'Near Miss'),
        ('minor_injury', 'Minor Injury'),
        ('major_injury', 'Major Injury'),
        ('property_damage', 'Property Damage'),
        ('environmental_spill', 'Environmental Spill'),
        ('fire_explosion', 'Fire/Explosion'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('corrective_action', 'Corrective Action'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='reported')
    location = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    reported_date = models.DateTimeField(default=timezone.now)
    incident_date = models.DateTimeField()
    affected_personnel = models.TextField(blank=True, null=True)
    root_cause = models.TextField(blank=True, null=True)
    corrective_actions = models.TextField(blank=True, null=True)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    investigation_lead = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investigated_incidents', null=True, blank=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    attachments = models.TextField(blank=True, null=True)  # Base64 encoded files

    class Meta:
        ordering = ['-reported_date']

    def __str__(self):
        return f"{self.title} - {self.reported_date}"


class HSEEquipment(models.Model):
    """HSE Equipment tracking"""
    EQUIPMENT_TYPES = [
        ('air_monitor', 'Air Quality Monitor'),
        ('water_treatment', 'Water Treatment System'),
        ('emission_control', 'Emission Control Equipment'),
        ('waste_management', 'Waste Management Equipment'),
        ('safety_equipment', 'Safety Equipment'),
        ('monitoring_device', 'Environmental Monitoring Device'),
    ]
    
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('out_of_service', 'Out of Service'),
        ('calibration_due', 'Calibration Due'),
        ('repair_needed', 'Repair Needed'),
    ]

    name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_TYPES)
    location = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='operational')
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    model_number = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    installation_date = models.DateField()
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    calibration_due = models.DateField(null=True, blank=True)
    responsible_person = models.ForeignKey(User, on_delete=models.CASCADE)
    specifications = models.TextField(blank=True, null=True)
    performance_metrics = models.TextField(blank=True, null=True)  # JSON field for metrics
    compliance_status = models.CharField(max_length=50, default='compliant')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class HSECompliance(models.Model):
    """HSE Compliance tracking"""
    COMPLIANCE_TYPES = [
        ('environmental_permit', 'Environmental Permit'),
        ('safety_regulation', 'Safety Regulation'),
        ('health_standard', 'Health Standard'),
        ('waste_management', 'Waste Management'),
        ('emission_control', 'Emission Control'),
        ('water_quality', 'Water Quality'),
    ]
    
    STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('pending_review', 'Pending Review'),
        ('under_investigation', 'Under Investigation'),
    ]

    title = models.CharField(max_length=255)
    compliance_type = models.CharField(max_length=50, choices=COMPLIANCE_TYPES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='compliant')
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    permit_number = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    responsible_person = models.ForeignKey(User, on_delete=models.CASCADE)
    requirements = models.TextField()
    current_status = models.TextField(blank=True, null=True)
    violations = models.TextField(blank=True, null=True)
    corrective_actions = models.TextField(blank=True, null=True)
    last_audit = models.DateField(null=True, blank=True)
    next_audit = models.DateField(null=True, blank=True)
    attachments = models.TextField(blank=True, null=True)  # Base64 encoded files

    class Meta:
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class HSETraining(models.Model):
    """HSE Training tracking"""
    TRAINING_TYPES = [
        ('safety_training', 'Safety Training'),
        ('environmental_training', 'Environmental Training'),
        ('compliance_training', 'Compliance Training'),
        ('equipment_training', 'Equipment Training'),
        ('emergency_response', 'Emergency Response'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    training_type = models.CharField(max_length=50, choices=TRAINING_TYPES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='scheduled')
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_trainings', null=True, blank=True)
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    certification_number = models.CharField(max_length=255, blank=True, null=True)
    certification_expiry = models.DateField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    attachments = models.TextField(blank=True, null=True)  # Base64 encoded files

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.title} - {self.employee.username}" 