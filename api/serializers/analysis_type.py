from rest_framework import serializers

from inspection_management.models import AnalysisType


class AnalysisTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnalysisType
        fields = "__all__"
