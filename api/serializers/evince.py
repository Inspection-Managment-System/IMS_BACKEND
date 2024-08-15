from rest_framework import serializers

from api.serializers import BusinessUnitSerializer as BUS
from api.serializers import InspectionAnalysisSerializer as IAS
from api.serializers import InspectionPointSerializer as IPS
from api.serializers import (ManyToManyRelatedFieldSerializer,
                             RelatedFieldSerializer)
from api.serializers import UserSerializer as US
from inspection_management.models import (BusinessUnit, Evince,
                                          InspectionAnalysis, InspectionPoint)
from users.models import User


class EvinceSerializer(serializers.ModelSerializer):
    business_unit = RelatedFieldSerializer(
        queryset=BusinessUnit.objects.all(), serializer=BUS
    )
    inspection_point = RelatedFieldSerializer(
        queryset=InspectionPoint.objects.all(), serializer=IPS
    )
    inspection_analyses = ManyToManyRelatedFieldSerializer(
        queryset=InspectionAnalysis.objects.all(), serializer=IAS
    )
    assigned_to = RelatedFieldSerializer(queryset=User.objects.all(), serializer=US)
    reviewed_by = RelatedFieldSerializer(queryset=User.objects.all(), serializer=US)

    class Meta:
        model = Evince
        fields = "__all__"
