from django.db import models

from .datalist import DataList


class DataListEntry(models.Model):
    description = models.CharField(max_length=255)
    data_list = models.ForeignKey(DataList, on_delete=models.CASCADE)
