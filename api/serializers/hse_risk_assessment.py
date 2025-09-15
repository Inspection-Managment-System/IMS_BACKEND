from rest_framework import serializers
from inspection_management.models import Evince, BusinessUnit, InspectionAnalysis, InspectionPoint
from users.models import User
from api.serializers import UserSerializer, BusinessUnitSerializer, InspectionAnalysisSerializer, InspectionPointSerializer


class HSERiskAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for HSE Risk Assessment Evince"""
    
    # Related field serializers - same as regular inspection
    inspection_point = InspectionPointSerializer(read_only=True)
    inspection_analyses = InspectionAnalysisSerializer(many=True, read_only=True)
    assigned_to = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    changed_by = UserSerializer(read_only=True)
    logged_by = UserSerializer(read_only=True)
    business_unit = BusinessUnitSerializer(read_only=True)
    
    # HSE Risk Assessment specific related fields
    hse_approved_by = UserSerializer(read_only=True)
    hse_mitigation_assigned_to = UserSerializer(read_only=True)
    hse_mitigation_department = BusinessUnitSerializer(read_only=True)
    
    # Write-only fields for creation/updates
    assigned_to_id = serializers.IntegerField(write_only=True, required=False)
    reviewed_by_id = serializers.IntegerField(write_only=True)
    changed_by_id = serializers.IntegerField(write_only=True)
    logged_by_id = serializers.IntegerField(write_only=True, required=False)
    hse_approved_by_id = serializers.IntegerField(write_only=True, required=False)
    hse_mitigation_assigned_to_id = serializers.IntegerField(write_only=True, required=False)
    hse_mitigation_department_id = serializers.IntegerField(write_only=True, required=False)
    
    # Computed fields
    risk_level_display = serializers.CharField(source='get_hse_risk_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    evince_type_display = serializers.CharField(source='get_evince_type_display', read_only=True)
    
    class Meta:
        model = Evince
        fields = [
            # Basic fields - same as regular inspection
            'id', 'name', 'description', 'evince_type', 'evince_type_display',
            'status', 'status_display', 'changed_on', 'changed_by', 'changed_by_id',
            'business_unit', 'inspection_point', 'inspection_analyses',
            'logged_by', 'logged_by_id', 'assigned_to', 'assigned_to_id', 
            'reviewed_by', 'reviewed_by_id', 'start_date_time', 'end_date_time', 
            'reassigned', 'crtical_instructions', 'crtical_instructions_file_name',
            
            # HSE Risk Assessment specific fields
            'hse_risk_assessment', 'hse_risk_notes', 'hse_risk_level', 'risk_level_display',
            'hse_risk_category', 'hse_inspection_date', 'hse_lims_reference_id',
            'hse_lims_status', 'hse_investigation_details', 'hse_mitigation_actions',
            'hse_approved_by', 'hse_approved_by_id', 'hse_approved_at',
            
            # Additional HSE Risk Workflow fields
            'hse_risk_valid', 'hse_out_of_spec_results', 'hse_observation_details',
            'hse_mitigation_department', 'hse_mitigation_department_id',
            'hse_mitigation_assigned_to', 'hse_mitigation_assigned_to_id',
            'hse_mitigation_target_date', 'hse_mitigation_evidence',
            'hse_mitigation_completed', 'hse_risk_closed', 'hse_risk_rejection_reason',
        ]
        read_only_fields = ['id', 'name', 'changed_on']
    
    def create(self, validated_data):
        """Handle creation of HSE Risk Assessment"""
        # Set default values for HSE Risk Assessment
        validated_data['evince_type'] = 'hse_risk_management'
        validated_data['status'] = 'Logged'
        
        # Handle related field IDs
        if 'assigned_to_id' in validated_data:
            validated_data['assigned_to'] = User.objects.get(id=validated_data.pop('assigned_to_id'))
        if 'reviewed_by_id' in validated_data:
            validated_data['reviewed_by'] = User.objects.get(id=validated_data.pop('reviewed_by_id'))
        if 'changed_by_id' in validated_data:
            validated_data['changed_by'] = User.objects.get(id=validated_data.pop('changed_by_id'))
        if 'logged_by_id' in validated_data:
            validated_data['logged_by'] = User.objects.get(id=validated_data.pop('logged_by_id'))
        if 'hse_approved_by_id' in validated_data:
            validated_data['hse_approved_by'] = User.objects.get(id=validated_data.pop('hse_approved_by_id'))
        if 'hse_mitigation_assigned_to_id' in validated_data:
            validated_data['hse_mitigation_assigned_to'] = User.objects.get(id=validated_data.pop('hse_mitigation_assigned_to_id'))
        if 'hse_mitigation_department_id' in validated_data:
            validated_data['hse_mitigation_department'] = BusinessUnit.objects.get(id=validated_data.pop('hse_mitigation_department_id'))
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Handle update of HSE Risk Assessment"""
        # Handle related field IDs
        if 'assigned_to_id' in validated_data:
            validated_data['assigned_to'] = User.objects.get(id=validated_data.pop('assigned_to_id'))
        if 'reviewed_by_id' in validated_data:
            validated_data['reviewed_by'] = User.objects.get(id=validated_data.pop('reviewed_by_id'))
        if 'changed_by_id' in validated_data:
            validated_data['changed_by'] = User.objects.get(id=validated_data.pop('changed_by_id'))
        if 'logged_by_id' in validated_data:
            validated_data['logged_by'] = User.objects.get(id=validated_data.pop('logged_by_id'))
        if 'hse_approved_by_id' in validated_data:
            validated_data['hse_approved_by'] = User.objects.get(id=validated_data.pop('hse_approved_by_id'))
        if 'hse_mitigation_assigned_to_id' in validated_data:
            validated_data['hse_mitigation_assigned_to'] = User.objects.get(id=validated_data.pop('hse_mitigation_assigned_to_id'))
        if 'hse_mitigation_department_id' in validated_data:
            validated_data['hse_mitigation_department'] = BusinessUnit.objects.get(id=validated_data.pop('hse_mitigation_department_id'))
        
        return super().update(instance, validated_data)


class HSERiskAssessmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating HSE Risk Assessment - similar to regular inspection creation"""
    
    class Meta:
        model = Evince
        fields = [
            'description', 'business_unit', 'inspection_point', 'assigned_to',
            'reviewed_by', 'changed_by', 'logged_by', 'start_date_time', 'end_date_time',
            'inspection_analyses', 'crtical_instructions', 'crtical_instructions_file_name',
            'reassigned'
        ]
        extra_kwargs = {
            'changed_by': {'required': False},
            'logged_by': {'required': False},
            'reviewed_by': {'required': False}
        }
    
    def create(self, validated_data):
        """Create HSE Risk Assessment with default values"""
        # Extract inspection_analyses before creating the instance
        inspection_analyses = validated_data.pop('inspection_analyses', [])
        
        # Set default values for HSE Risk Assessment
        validated_data['evince_type'] = 'hse_risk_management'
        validated_data['status'] = 'Logged'
        
        # Create the instance
        instance = super().create(validated_data)
        
        # Add inspection_analyses after creation
        if inspection_analyses:
            instance.inspection_analyses.set(inspection_analyses)
        
        return instance


class HSERiskAssessmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating HSE Risk Assessment workflow states"""
    
    class Meta:
        model = Evince
        fields = [
            'hse_risk_level', 'hse_risk_category', 'hse_risk_notes',
            'hse_observation_details', 'hse_out_of_spec_results',
            'hse_risk_valid', 'hse_mitigation_department', 'hse_mitigation_assigned_to',
            'hse_mitigation_target_date', 'hse_mitigation_actions',
            'hse_mitigation_evidence', 'hse_mitigation_completed',
            'hse_risk_closed', 'hse_risk_rejection_reason', 'status'
        ]
    
    def validate_hse_out_of_spec_results(self, value):
        """Validate out-of-spec results format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Out-of-spec results must be a list")
        
        for result in value:
            if not isinstance(result, dict):
                raise serializers.ValidationError("Each result must be a dictionary")
            required_fields = ['parameter', 'value', 'spec', 'status']
            for field in required_fields:
                if field not in result:
                    raise serializers.ValidationError(f"Missing required field: {field}")
        
        return value
