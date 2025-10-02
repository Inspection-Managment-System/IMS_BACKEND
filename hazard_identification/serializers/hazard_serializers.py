from rest_framework import serializers
from hazard_identification.models import HazardIdentification, HazardEvidence, HazardCategory
from inspection_management.models import BusinessUnit, ExternalDepartment
from users.models.user import User


class HazardCategorySerializer(serializers.ModelSerializer):
    """Serializer for hazard categories"""
    
    class Meta:
        model = HazardCategory
        fields = '__all__'


class HazardEvidenceSerializer(serializers.ModelSerializer):
    """Serializer for hazard evidence photos"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    filename = serializers.CharField(read_only=True)
    
    class Meta:
        model = HazardEvidence
        fields = [
            'id', 'evidence_type', 'image', 'description', 
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'filename'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']


class HazardIdentificationListSerializer(serializers.ModelSerializer):
    """Serializer for hazard list view - optimized for performance"""
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    managed_by_name = serializers.CharField(source='managed_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_department_name = serializers.CharField(source='assigned_department.name', read_only=True)
    business_unit_name = serializers.CharField(source='business_unit.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_color = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = HazardIdentification
        fields = [
            'id', 'serial_number', 'hazard_description', 'location',
            'business_unit', 'business_unit_name', 'category', 'category_name',
            'severity_level', 'priority_level', 'status', 'status_color',
            'reported_by', 'reported_by_name', 'managed_by', 'managed_by_name',
            'assigned_to', 'assigned_to_name', 'assigned_department', 'assigned_department_name', 'reviewed_by',
            'reported_date', 'target_completion_date', 'actual_completion_date',
            'last_updated', 'is_overdue', 'days_overdue'
        ]


class HazardIdentificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new hazards"""
    
    class Meta:
        model = HazardIdentification
        fields = [
            'id', 'hazard_description', 'location', 'business_unit', 'category',
            'severity_level', 'priority_level', 'recommended_controls',
            'estimated_resolution_time', 'additional_notes', 'managed_by', 'assigned_to'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        # Set the reported_by to the current user
        validated_data['reported_by'] = self.context['request'].user
        
        # Automatically set status to AssignedToInspector if an inspector is assigned
        if validated_data.get('assigned_to'):
            validated_data['status'] = 'AssignedToInspector'
        
        return super().create(validated_data)


class HazardIdentificationSerializer(serializers.ModelSerializer):
    """Full serializer for hazard details"""
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_department_name = serializers.CharField(source='assigned_department.name', read_only=True)
    business_unit_name = serializers.CharField(source='business_unit.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    status_color = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    # Include evidence photos
    evidence = HazardEvidenceSerializer(many=True, read_only=True)
    before_photos = serializers.SerializerMethodField()
    after_photos = serializers.SerializerMethodField()
    
    class Meta:
        model = HazardIdentification
        fields = '__all__'
        read_only_fields = [
            'serial_number', 'reported_by', 'reported_date', 
            'actual_completion_date', 'created_at', 'updated_at'
        ]
    
    def get_before_photos(self, obj):
        """Get before photos for this hazard"""
        before_evidence = obj.evidence.filter(evidence_type='before')
        return HazardEvidenceSerializer(before_evidence, many=True).data
    
    def get_after_photos(self, obj):
        """Get after photos for this hazard"""
        after_evidence = obj.evidence.filter(evidence_type='after')
        return HazardEvidenceSerializer(after_evidence, many=True).data


class HazardAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning hazards to departments/users"""
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    assigned_department = serializers.PrimaryKeyRelatedField(
        queryset=ExternalDepartment.objects.all(),
        required=False,
        allow_null=True
    )
    target_completion_date = serializers.DateTimeField(required=False)
    assignment_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        # At least one assignment must be provided
        if not data.get('assigned_to') and not data.get('assigned_department'):
            raise serializers.ValidationError(
                "Either assigned_to or assigned_department must be provided"
            )
        return data


class HazardStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating hazard status"""
    status = serializers.ChoiceField(choices=HazardIdentification.STATUS_CHOICES)
    status_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        """Validate status transition"""
        instance = self.context.get('instance')
        if instance:
            current_status = instance.status
            # Define valid status transitions
            valid_transitions = {
                'Logged': ['InspectorReview'],
                'InspectorReview': ['ManagerAssignment'],
                'ManagerAssignment': ['InProgress'],
                'InProgress': ['Done'],
                'Done': []  # Final status
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from {current_status} to {value}"
                )
        
        return value
