from rest_framework import serializers

from api.serializers import DataGroupSerializer as DGS
from api.serializers import RelatedFieldSerializer as RFS
from inspection_management.models import DataGroup, Location


class LocationSerializer(serializers.ModelSerializer):
    group = RFS(queryset=DataGroup.objects.all(), serializer=DGS)

    class Meta:
        model = Location
        fields = "__all__"
