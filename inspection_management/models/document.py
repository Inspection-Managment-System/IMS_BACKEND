from django.db import models

from users.models import User

from .equipment import Equipment
from .site import Site


class Document(models.Model):
    CATEGORY_CHOICES = [
        ("inspection", "Inspection Report"),
        ("certificate", "Test Certificate"),
        ("sop", "Standard Operating Procedure"),
        ("maintenance", "Maintenance & Calibration Log"),
        ("compliance", "Compliance & Regulatory"),
    ]

    file = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    equipment = models.ForeignKey(
        Equipment, on_delete=models.SET_NULL, null=True, blank=True
    )
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateField(auto_now_add=True)
    document_expiry = models.DateField(null=True, blank=True)
    version = models.IntegerField(default=1)
    approved = models.BooleanField(default=False)
    previous_version = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-upload_date"]
