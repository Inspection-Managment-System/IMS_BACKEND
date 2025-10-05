from django.contrib import admin
from .models import HazardIdentification, HazardEvidence, HazardCategory

@admin.register(HazardIdentification)
class HazardIdentificationAdmin(admin.ModelAdmin):
    list_display = [
        'serial_number', 'hazard_description', 'severity_level', 'priority_level', 
        'status', 'reported_date', 'target_completion_date', 'reported_by', 
        'assigned_to', 'category', 'location'
    ]
    list_filter = [
        'status', 'severity_level', 'priority_level', 'category', 
        'reported_date', 'target_completion_date', 'assigned_department'
    ]
    search_fields = [
        'serial_number', 'hazard_description', 'location', 
        'reported_by__username', 'assigned_to__username'
    ]
    readonly_fields = ['serial_number', 'created_at', 'updated_at', 'last_updated']
    date_hierarchy = 'reported_date'
    ordering = ['-reported_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('serial_number', 'hazard_description', 'location', 'category')
        }),
        ('Risk Assessment', {
            'fields': ('severity_level', 'priority_level', 'recommended_controls')
        }),
        ('Timeline', {
            'fields': ('reported_date', 'target_completion_date', 'actual_completion_date', 'estimated_resolution_time')
        }),
        ('Assignment', {
            'fields': ('reported_by', 'assigned_to', 'assigned_department', 'business_unit', 'managed_by')
        }),
        ('Status & Review', {
            'fields': ('status', 'reviewed_by', 'manager_decision', 'manager_review_notes', 'reassignment_notes', 'rejection_reason')
        }),
        ('Additional Information', {
            'fields': ('additional_notes', 'created_at', 'updated_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(HazardEvidence)
class HazardEvidenceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'hazard', 'evidence_type', 'uploaded_by', 'uploaded_at', 'description'
    ]
    list_filter = ['evidence_type', 'uploaded_at', 'uploaded_by']
    search_fields = ['hazard__serial_number', 'description', 'uploaded_by__username']
    readonly_fields = ['uploaded_at']
    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']

@admin.register(HazardCategory)
class HazardCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
