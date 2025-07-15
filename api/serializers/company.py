from rest_framework import serializers

from inspection_management.models import Company, DataGroup


class ComapnySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = "__all__"


class ComapnyGetSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        queryset=DataGroup.objects.all(), slug_field="name"
    )

    class Meta:
        model = Company
        fields = "__all__"
