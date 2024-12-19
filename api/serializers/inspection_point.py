from rest_framework import serializers

from api.serializers import BusinessUnitSerializer as BUS
from api.serializers import RelatedFieldSerializer as RFS
from inspection_management.models import BusinessUnit, InspectionPoint


class InspectionPointSerializer(serializers.ModelSerializer):
    business_unit = RFS(queryset=BusinessUnit.objects.all(), serializer=BUS)

    class Meta:
        model = InspectionPoint
        fields = "__all__"
