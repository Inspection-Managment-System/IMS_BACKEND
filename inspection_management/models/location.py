from django.db import models

from users.models.user import User

from .datagroup import DataGroup


class Location(models.Model):
    name = models.CharField(max_length=25)
    description = models.CharField(max_length=255)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    building = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=25, blank=True, null=True)
    contact = models.CharField(max_length=25, blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
