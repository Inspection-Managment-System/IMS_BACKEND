from django.db import models


class DataGroup(models.Model):
    name = models.CharField(max_length=255)
    attachment = models.FileField(
        upload_to="datagroup_attachments/", blank=True, null=True
    )

    def __str__(self):
        return self.name
