from rest_framework import serializers
from inspection_management.models import RiskLevel, RiskCategory, HSEObservationType


class RiskLevelSerializer(serializers.ModelSerializer):
    """Serializer for Risk Levels"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = RiskLevel
        fields = ['id', 'name', 'value', 'description', 'order', 'group', 'group_name', 'changed_by', 'changed_on']
        read_only_fields = ['id', 'changed_by', 'changed_on', 'group_name']


class RiskCategorySerializer(serializers.ModelSerializer):
    """Serializer for Risk Categories"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = RiskCategory
        fields = ['id', 'name', 'value', 'description', 'order', 'group', 'group_name', 'changed_by', 'changed_on']
        read_only_fields = ['id', 'changed_by', 'changed_on', 'group_name']


class HSEObservationTypeSerializer(serializers.ModelSerializer):
    """Serializer for HSE Observation Types"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = HSEObservationType
        fields = ['id', 'name', 'value', 'description', 'order', 'group', 'group_name', 'changed_by', 'changed_on']
        read_only_fields = ['id', 'changed_by', 'changed_on', 'group_name']

