from rest_framework import serializers

from api.serializers import DataGroupSerializer as DGS
from api.serializers import EquipmentTypeSerializer as ETS
from api.serializers import LocationSerializer as LS
from api.serializers import RelatedFieldSerializer as RFS
from inspection_management.models import (DataGroup, Equipment, EquipmentType,
                                          Location)


class EquipmentSerializer(serializers.ModelSerializer):
    group = RFS(queryset=DataGroup.objects.all(), serializer=DGS)
    location = RFS(queryset=Location.objects.all(), serializer=LS)
    equipment_type = RFS(queryset=EquipmentType.objects.all(), serializer=ETS)

    class Meta:
        model = Equipment
        fields = "__all__"
