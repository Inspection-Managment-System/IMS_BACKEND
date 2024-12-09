from io import BytesIO

import qrcode
from django.core.files import File
from django.db import models

from users.models.user import User

from .business_unit import BusinessUnit
from .datagroup import DataGroup


class InspectionPoint(models.Model):
    RISK_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    qr_code = models.TextField(blank=True, null=True)
    flammability = models.CharField(max_length=10, choices=RISK_CHOICES, default="Low")
    health_risk = models.CharField(max_length=10, choices=RISK_CHOICES, default="Low")
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.id))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = BytesIO()
        img.save(img_buffer)
        img_buffer.seek(0)

        self.qr_code.save(
            f"qr_code_{self.name}_{self.id}.png", File(img_buffer), save=True
        )
