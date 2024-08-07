from rest_framework import serializers

from api.serializers import GroupSerializer as GS
from api.serializers import RelatedFieldSerializer
from inspection_management.models import AnalysisType, DataGroup


class AnalysisTypeSerializer(serializers.ModelSerializer):
    group = RelatedFieldSerializer(queryset=DataGroup.objects.all(), serializer=GS)

    class Meta:
        model = AnalysisType
        fields = "__all__"
