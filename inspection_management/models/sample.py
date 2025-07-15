from django.db import models


class Sample(models.Model):
    SAMPLE_NUMBER = models.IntegerField(primary_key=True)
    SAMPLE_VOLUME = models.FloatField(null=True, blank=True)
    SAMPLE_UNITS = models.CharField(max_length=255, null=True, blank=True)
    SAMPLE_TYPE = models.CharField(max_length=255, null=True, blank=True)
    CONTAINER_TYPE = models.CharField(max_length=255, null=True, blank=True)
    TEXT_ID = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "SAMPLE"
        managed = False
