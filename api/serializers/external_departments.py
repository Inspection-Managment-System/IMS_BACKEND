from rest_framework import serializers
from inspection_management.models import ExternalDepartment, ExternalDepartmentAssignment
from users.models import User


class ExternalDepartmentSerializer(serializers.ModelSerializer):
    """Serializer for External Department"""
    
    # Related field serializers
    created_by = serializers.StringRelatedField(read_only=True)
    
    # Computed fields
    department_type_display = serializers.CharField(source='get_department_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_assignments_count = serializers.ReadOnlyField()
    is_available_for_assignment = serializers.ReadOnlyField()
    
    class Meta:
        model = ExternalDepartment
        fields = [
            'id', 'name', 'department_type', 'department_type_display',
            'description', 'external_system_url', 'external_system_id',
            'contact_person', 'contact_email', 'contact_phone',
            'capabilities', 'specializations', 'status', 'status_display',
            'is_available', 'max_concurrent_assignments',
            'current_assignments_count', 'is_available_for_assignment',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_assignments_count', 'is_available_for_assignment']


class ExternalDepartmentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for External Department Assignment"""
    
    # Related field serializers
    evince = serializers.StringRelatedField(read_only=True)
    external_department = serializers.StringRelatedField(read_only=True)
    assigned_by = serializers.StringRelatedField(read_only=True)
    
    # Computed fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ExternalDepartmentAssignment
        fields = [
            'id', 'evince', 'external_department', 'assigned_by',
            'assigned_at', 'target_completion_date', 'external_task_id',
            'external_status', 'last_sync_at', 'status', 'status_display',
            'notes', 'external_response', 'completion_notes',
            'mitigation_actions', 'evidence_data', 'cost_incurred'
        ]
        read_only_fields = ['id', 'assigned_at', 'last_sync_at']


class ExternalDepartmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating External Department"""
    
    class Meta:
        model = ExternalDepartment
        fields = [
            'name', 'department_type', 'description', 'external_system_url',
            'external_system_id', 'contact_person', 'contact_email',
            'contact_phone', 'capabilities', 'specializations', 'status',
            'is_available', 'max_concurrent_assignments'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExternalDepartmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating External Department"""
    
    class Meta:
        model = ExternalDepartment
        fields = [
            'name', 'description', 'external_system_url', 'contact_person',
            'contact_email', 'contact_phone', 'capabilities', 'specializations',
            'status', 'is_available', 'max_concurrent_assignments'
        ]
