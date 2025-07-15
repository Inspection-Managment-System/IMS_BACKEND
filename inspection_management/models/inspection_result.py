from django.db import models

from inspection_management.models import Evince, InspectionTest
from users.models.user import User


class InspectionResult(models.Model):
    STATUS_CHOICES = [
        ("Incomplete", "Incomplete"),
        ("Completed", "Completed"),
    ]
    evince = models.ForeignKey(Evince, on_delete=models.CASCADE)
    inspection_test = models.ForeignKey(InspectionTest, on_delete=models.CASCADE)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=25, choices=STATUS_CHOICES, default="Incomplete"
    )
    entered_value = models.CharField(max_length=255, null=True, blank=True)
    previous_value = models.CharField(max_length=255, null=True, blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)
    sample_required = models.BooleanField(default=False)
    sample_content = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.evince.name}_{self.inspection_test.pk}_{self.pk}"
