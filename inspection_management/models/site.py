from django.db import models

from users.models.user import User

from .company import Company
from .datagroup import DataGroup


class Site(models.Model):
    name = models.CharField(max_length=25)
    description = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    changed_on = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(DataGroup, on_delete=models.CASCADE)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
