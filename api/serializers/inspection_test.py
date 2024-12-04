from rest_framework import serializers

from api.serializers import EvinceSerializer as ES
from api.serializers import InspectionAnalysisSerializer as IAS
from api.serializers import RelatedFieldSerializer
from inspection_management.models import (Evince, InspectionAnalysis,
                                          InspectionTest)


class InspectionTestSerializer(serializers.ModelSerializer):
    evince = RelatedFieldSerializer(queryset=Evince.objects.all(), serializer=ES)
    inspection_analysis = RelatedFieldSerializer(
        queryset=InspectionAnalysis.objects.all(),
        serializer=IAS,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = InspectionTest
        fields = "__all__"
