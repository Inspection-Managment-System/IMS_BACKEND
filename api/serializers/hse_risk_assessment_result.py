from rest_framework import serializers
from inspection_management.models import HSERiskAssessmentResult, Evince
from users.models import User


class HSERiskAssessmentResultSerializer(serializers.ModelSerializer):
    """
    Serializer for HSE Risk Assessment Results
    """
    evince_id = serializers.IntegerField(source='evince.id', read_only=True)
    evince_name = serializers.CharField(source='evince.name', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = HSERiskAssessmentResult
        fields = [
            'id',
            'evince_id',
            'evince_name',
            'parameter_name',
            'parameter_value',
            'parameter_comments',
            'parameter_status',
            'risk_level',
            'risk_category',
            'risk_notes',
            'observation_details',
            'risk_valid',
            'mitigation_actions',
            'mitigation_target_date',
            'mitigation_evidence',
            'mitigation_completed',
            'risk_closed',
            'created_on',
            'changed_on',
            'changed_by_username',
        ]
        read_only_fields = ['id', 'created_on', 'changed_on', 'changed_by_username']
    
    def create(self, validated_data):
        """
        Create a new HSE Risk Assessment Result
        """
        validated_data['changed_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update an existing HSE Risk Assessment Result
        """
        validated_data['changed_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class HSERiskAssessmentResultCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating HSE Risk Assessment Results
    """
    class Meta:
        model = HSERiskAssessmentResult
        fields = [
            'evince',
            'parameter_name',
            'parameter_value',
            'parameter_comments',
            'parameter_status',
            'risk_level',
            'risk_category',
            'risk_notes',
            'observation_details',
            'risk_valid',
            'mitigation_actions',
            'mitigation_target_date',
            'mitigation_evidence',
            'mitigation_completed',
            'risk_closed',
        ]
    
    def create(self, validated_data):
        """
        Create a new HSE Risk Assessment Result
        """
        validated_data['changed_by'] = self.context['request'].user
        return super().create(validated_data)


class HSERiskAssessmentResultUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating HSE Risk Assessment Results
    """
    class Meta:
        model = HSERiskAssessmentResult
        fields = [
            'parameter_value',
            'parameter_comments',
            'parameter_status',
            'risk_level',
            'risk_category',
            'risk_notes',
            'observation_details',
            'risk_valid',
            'mitigation_actions',
            'mitigation_target_date',
            'mitigation_evidence',
            'mitigation_completed',
            'risk_closed',
        ]
    
    def update(self, instance, validated_data):
        """
        Update an existing HSE Risk Assessment Result
        """
        validated_data['changed_by'] = self.context['request'].user
        return super().update(instance, validated_data)
