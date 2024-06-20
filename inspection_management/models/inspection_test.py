from django.db import models

from inspection_management.models import Evince, InspectionAnalysis
from users.models.user import User


class InspectionTest(models.Model):
    evince = models.ForeignKey(Evince, on_delete=models.CASCADE)
    inspection_analysis = models.ForeignKey(
        InspectionAnalysis, on_delete=models.CASCADE
    )
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.evince.name}_{self.inspection_analysis.name}_{self.pk}"
