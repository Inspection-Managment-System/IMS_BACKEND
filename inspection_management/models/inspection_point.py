import base64
from io import BytesIO

import qrcode
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

        qr_data = f"ID: {self.id}\nName: {self.name}\nBusiness Unit: {self.business_unit}\nGroup: {self.group}"
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        base64_string = base64.b64encode(img_buffer.read()).decode("utf-8")

        self.qr_code = base64_string
        self.save()


@receiver(post_save, sender=InspectionPoint)
def generate_qr_code_after_save(sender, instance, created, **kwargs):
    if created:
        instance.generate_qr_code()
