from rest_framework import serializers

from inspection_management.models import DataGroup


class DataGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataGroup
        fields = "__all__"
