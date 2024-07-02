from django.db import models

from inspection_management.models.equipment_type import EquipmentType
from inspection_management.models.location import Location
from users.models.user import User

from .datagroup import DataGroup


class Equipment(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=255)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    callibration_date = models.DateTimeField()
    callibration_expiry = models.DateTimeField()
    operator = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="equipment_operator",
    )
    serial_no = models.CharField(max_length=100)
    asset_number = models.CharField(max_length=100, blank=True, null=True)
    equipment_type = models.ForeignKey(
        EquipmentType, blank=True, null=True, on_delete=models.CASCADE
    )
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
