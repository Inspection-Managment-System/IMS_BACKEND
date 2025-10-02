from django.db import models
from django.conf import settings
import os


def hazard_evidence_upload_path(instance, filename):
    """Generate upload path for hazard evidence photos"""
    hazard_id = instance.hazard.id if instance.hazard else 'unknown'
    evidence_type = instance.evidence_type
    return f'hazard_evidence/{hazard_id}/{evidence_type}/{filename}'


class HazardEvidence(models.Model):
    """Photo evidence for hazards - before and after photos"""
    
    EVIDENCE_TYPE_CHOICES = [
        ('before', 'Before'),
        ('after', 'After'),
        ('initial', 'Initial'),
        ('admin', 'Admin'),
        ('assessment', 'Assessment'),
        ('inspector', 'Inspector'),
    ]
    
    hazard = models.ForeignKey(
        'HazardIdentification', 
        on_delete=models.CASCADE, 
        related_name='evidence'
    )
    evidence_type = models.CharField(
        max_length=10, 
        choices=EVIDENCE_TYPE_CHOICES,
        help_text="Whether this is a 'before' or 'after' photo"
    )
    image = models.ImageField(
        upload_to=hazard_evidence_upload_path,
        help_text="Photo evidence of the hazard"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this photo shows"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_hazard_evidence'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Hazard Evidence"
        verbose_name_plural = "Hazard Evidence"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.hazard.hazard_description[:50]} - {self.get_evidence_type_display()}"
    
    @property
    def filename(self):
        """Get the filename without path"""
        return os.path.basename(self.image.name)
