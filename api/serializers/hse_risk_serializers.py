from rest_framework import serializers
from inspection_management.models.evince import Evince
from inspection_management.models.business_unit import BusinessUnit
from inspection_management.models.inspection_point import InspectionPoint
from users.models.user import User


class HSERiskEvinceSerializer(serializers.ModelSerializer):
    """Serializer for HSE Risk Management evinces"""
    
    business_unit_name = serializers.CharField(source='business_unit.name', read_only=True)
    inspection_point_name = serializers.CharField(source='inspection_point.name', read_only=True)
    logged_by_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    evince_type_display = serializers.CharField(source='get_evince_type_display', read_only=True)
    
    class Meta:
        model = Evince
        fields = [
            'id', 'name', 'description', 'evince_type', 'evince_type_display',
            'business_unit', 'business_unit_name', 'inspection_point', 'inspection_point_name',
            'logged_by', 'logged_by_name', 'reviewed_by', 'reviewed_by_name',
            'assigned_to', 'assigned_to_name', 'approved_by', 'approved_by_name',
            'status', 'status_display', 'changed_on', 'changed_by',
            'crtical_instructions', 'start_date_time', 'end_date_time',
            
            # HSE Risk Management specific fields
            'hse_risk_assessment', 'hse_risk_notes', 'hse_risk_level',
            'hse_risk_category', 'hse_inspection_date', 'hse_lims_reference_id',
            'hse_lims_status', 'hse_investigation_details', 'hse_mitigation_actions',
            'hse_approved_by', 'hse_approved_at'
        ]
        read_only_fields = ['id', 'name', 'changed_on', 'changed_by']
    
    def get_logged_by_name(self, obj):
        if obj.logged_by:
            return f"{obj.logged_by.first_name} {obj.logged_by.last_name}".strip() or obj.logged_by.username
        return None
    
    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.username
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None
    
    def get_approved_by_name(self, obj):
        if obj.hse_approved_by:
            return f"{obj.hse_approved_by.first_name} {obj.hse_approved_by.last_name}".strip() or obj.hse_approved_by.username
        return None


class HSERiskEvinceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating HSE Risk Management evinces"""
    
    class Meta:
        model = Evince
        fields = [
            'description', 'business_unit', 'inspection_point', 'reviewed_by',
            'inspection_date', 'risk_category', 'instructions', 'start_date_time', 'end_date_time'
        ]
    
    def validate(self, data):
        """Validate HSE Risk evince data"""
        if not data.get('business_unit'):
            raise serializers.ValidationError("Business unit is required")
        
        if not data.get('inspection_point'):
            raise serializers.ValidationError("Inspection point is required")
        
        if not data.get('reviewed_by'):
            raise serializers.ValidationError("Inspector (reviewed_by) is required")
        
        return data
    
    def create(self, validated_data):
        """Create HSE Risk evince"""
        from api.services.hse_risk_evince_service import HSERiskEvinceService
        
        user = self.context['request'].user
        validated_data['evince_type'] = 'hse_risk_management'
        
        return HSERiskEvinceService.create_hse_risk_evince(validated_data, user)


class HSERiskAssessmentSerializer(serializers.Serializer):
    """Serializer for HSE Risk assessment data"""
    
    risk_level = serializers.ChoiceField(choices=[
        ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')
    ])
    risk_category = serializers.CharField(max_length=50)
    notes = serializers.CharField(allow_blank=True)
    parameters = serializers.DictField(child=serializers.BooleanField())
    risk_identified = serializers.BooleanField()


class HSERiskInspectorReviewSerializer(serializers.Serializer):
    """Serializer for inspector review"""
    
    risk_assessment = HSERiskAssessmentSerializer()
    comments = serializers.CharField(allow_blank=True)


class HSERiskManagerAssignmentSerializer(serializers.Serializer):
    """Serializer for manager assignment"""
    
    assigned_to_id = serializers.IntegerField()
    assignment_notes = serializers.CharField(allow_blank=True)


class HSERiskLIMSCompletionSerializer(serializers.Serializer):
    """Serializer for LIMS completion callback"""
    
    lims_reference_id = serializers.CharField(max_length=100)
    lims_status = serializers.CharField(max_length=50)
    investigation_details = serializers.CharField()
    mitigation_actions = serializers.CharField()


class HSERiskManagerApprovalSerializer(serializers.Serializer):
    """Serializer for manager approval"""
    
    approval_status = serializers.ChoiceField(choices=[
        ('approved', 'Approved'), ('rejected', 'Rejected')
    ])
    approval_notes = serializers.CharField(allow_blank=True)


class HSERiskDashboardStatsSerializer(serializers.Serializer):
    """Serializer for HSE Risk dashboard statistics"""
    
    total_risks = serializers.IntegerField()
    logged = serializers.IntegerField()
    inspector_review = serializers.IntegerField()
    risk_validated = serializers.IntegerField()
    manager_assignment = serializers.IntegerField()
    lims_in_progress = serializers.IntegerField()
    lims_completed = serializers.IntegerField()
    manager_approval = serializers.IntegerField()
    completed = serializers.IntegerField()
    rejected = serializers.IntegerField()

