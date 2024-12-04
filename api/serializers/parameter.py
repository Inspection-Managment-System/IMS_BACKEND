from rest_framework import serializers

from api.serializers import GroupSerializer as GS
from api.serializers import InspectionAnalysisSerializer as IAS
from api.serializers import RelatedFieldSerializer
from api.serializers import UnitSerializer as US
from inspection_management.models import (DataGroup, InspectionAnalysis,
                                          Parameter, Unit)


class ParameterSerializer(serializers.ModelSerializer):
    group = RelatedFieldSerializer(queryset=DataGroup.objects.all(), serializer=GS)
    inspection_analysis = RelatedFieldSerializer(
        queryset=InspectionAnalysis.objects.all(), serializer=IAS
    )
    unit = RelatedFieldSerializer(queryset=Unit.objects.all(), serializer=US)

    class Meta:
        model = Parameter
        fields = "__all__"
