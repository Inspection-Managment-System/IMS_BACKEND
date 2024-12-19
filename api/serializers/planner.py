from rest_framework import serializers

from api.serializers import BusinessUnitSerializer as BUS
from api.serializers import InspectionAnalysisSerializer as IAS
from api.serializers import InspectionPointSerializer as IPS
from api.serializers import (ManyToManyRelatedFieldSerializer,
                             RelatedFieldSerializer)
from inspection_management.models import (BusinessUnit, InspectionAnalysis,
                                          InspectionPoint, Planner)


class PlannerSerializer(serializers.ModelSerializer):
    evince_business_unit = RelatedFieldSerializer(
        queryset=BusinessUnit.objects.all(), serializer=BUS
    )
    evince_inspection_point = RelatedFieldSerializer(
        queryset=InspectionPoint.objects.all(), serializer=IPS
    )
    evince_inspection_analyses = ManyToManyRelatedFieldSerializer(
        queryset=InspectionAnalysis.objects.all(), serializer=IAS
    )

    class Meta:
        model = Planner
        fields = "__all__"
