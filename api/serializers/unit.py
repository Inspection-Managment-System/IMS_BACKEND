from rest_framework import serializers

from inspection_management.models import Unit


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = "__all__"
