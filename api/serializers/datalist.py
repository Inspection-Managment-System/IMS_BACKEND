from rest_framework import serializers

from inspection_management.models import DataList


class DataListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataList
        fields = "__all__"
