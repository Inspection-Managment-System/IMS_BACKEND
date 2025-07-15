from rest_framework import serializers

from api.serializers import GroupSerializer as GS
from api.serializers import RelatedFieldSerializer
from inspection_management.models import DataGroup, Unit


class UnitSerializer(serializers.ModelSerializer):
    group = RelatedFieldSerializer(queryset=DataGroup.objects.all(), serializer=GS)

    class Meta:
        model = Unit
        fields = "__all__"
