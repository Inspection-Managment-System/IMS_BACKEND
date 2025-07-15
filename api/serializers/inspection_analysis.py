from rest_framework import serializers

from api.serializers import AnalysisTypeSerializer as AS
from api.serializers import EquipmentSerializer as ES
from api.serializers import GroupSerializer as GS
from api.serializers import LocationSerializer as LS
from api.serializers import RelatedFieldSerializer
from inspection_management.models import (AnalysisType, DataGroup, Equipment,
                                          InspectionAnalysis, Location)


class InspectionAnalysisSerializer(serializers.ModelSerializer):
    group = RelatedFieldSerializer(queryset=DataGroup.objects.all(), serializer=GS)
    equipment = RelatedFieldSerializer(
        queryset=Equipment.objects.all(), serializer=ES, required=False, allow_null=True
    )
    analysis_type = RelatedFieldSerializer(
        queryset=AnalysisType.objects.all(), serializer=AS
    )
    location = RelatedFieldSerializer(queryset=Location.objects.all(), serializer=LS)

    class Meta:
        model = InspectionAnalysis
        fields = "__all__"
