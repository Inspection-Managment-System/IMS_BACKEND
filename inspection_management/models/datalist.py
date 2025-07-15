from django.db import models


class DataList(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data = models.TextField(null=True, blank=True)
