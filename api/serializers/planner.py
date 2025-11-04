from rest_framework import serializers

from api.serializers import BusinessUnitSerializer as BUS
from api.serializers import InspectionAnalysisSerializer as IAS
from api.serializers import InspectionPointSerializer as IPS
from api.serializers import (ManyToManyRelatedFieldSerializer,
                             RelatedFieldSerializer)
from inspection_management.models import (BusinessUnit, InspectionAnalysis,
                                          InspectionPoint, Planner, Parameter)
from users.models import User


class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple user serializer for planner fields"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SimpleParameterSerializer(serializers.ModelSerializer):
    """Simple parameter serializer for planner"""
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = Parameter
        fields = ['id', 'name', 'description', 'unit_name', 'min_value', 'max_value', 'avg_value', 'string_value']


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
    
    # Return parameters as full objects
    parameters = SimpleParameterSerializer(source='evince_parameters', many=True, read_only=True)
    
    # Return full user objects for both reviewed_by and assigned_to
    reviewed_by = SimpleUserSerializer(read_only=True)
    assigned_to = SimpleUserSerializer(source='evince_assigned_to', read_only=True)
    
    # For write operations, accept IDs
    reviewed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewed_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='evince_assigned_to',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Planner
        fields = "__all__"
