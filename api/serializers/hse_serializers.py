from rest_framework import serializers
from inspection_management.models.hse_workflow_models import HSEObservation, HSEWorkflowHistory, HSEEvidence


class HSEObservationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.get_full_name', read_only=True)
    department_name = serializers.CharField(source='affected_department.name', read_only=True)
    
    class Meta:
        model = HSEObservation
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'affected_department': {'required': False},
            'workflow_state': {'required': False},
            'risk_category': {'required': False}
        }
    
    def create(self, validated_data):
        """Handle creation with default values for missing fields"""
        try:
            # Set default values for required fields if not provided
            if 'affected_department' not in validated_data:
                # Get the first available business unit as default
                from inspection_management.models.business_unit import BusinessUnit
                
                default_dept = BusinessUnit.objects.first()
                if default_dept:
                    validated_data['affected_department'] = default_dept
                else:
                    raise serializers.ValidationError("No business units available. Please create a business unit first in the admin panel.")
            
            if 'workflow_state' not in validated_data:
                validated_data['workflow_state'] = 'DRAFT'
            
            if 'risk_category' not in validated_data:
                validated_data['risk_category'] = 'Safety'
            
            print(f"Creating observation with data: {validated_data}")
            return super().create(validated_data)
        except Exception as e:
            print(f"Error creating observation: {e}")
            raise


class HSEWorkflowHistorySerializer(serializers.ModelSerializer):
    action_by_name = serializers.CharField(source='action_by.get_full_name', read_only=True)
    observation_title = serializers.CharField(source='observation.title', read_only=True)
    
    class Meta:
        model = HSEWorkflowHistory

        fields = '__all__'
        read_only_fields = ['action_by', 'created_at']


class HSEEvidenceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    observation_title = serializers.CharField(source='observation.title', read_only=True)
    
    class Meta:
        model = HSEEvidence
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'uploaded_at']