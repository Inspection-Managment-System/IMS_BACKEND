from django.db import models


class DataGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
