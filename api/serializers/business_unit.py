from rest_framework import serializers

from api.serializers import RelatedFieldSerializer as RFS
from api.serializers import SiteSerializer as SS
from inspection_management.models import BusinessUnit, Site


class BusinessUnitSerializer(serializers.ModelSerializer):
    site = RFS(queryset=Site.objects.all(), serializer=SS)

    class Meta:
        model = BusinessUnit
        fields = "__all__"
