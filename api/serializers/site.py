from rest_framework import serializers

from api.serializers import ComapnySerializer as CS
from api.serializers import RelatedFieldSerializer
from inspection_management.models import Company, Site


class SiteSerializer(serializers.ModelSerializer):
    company = RelatedFieldSerializer(queryset=Company.objects.all(), serializer=CS)

    class Meta:
        model = Site
        fields = "__all__"
