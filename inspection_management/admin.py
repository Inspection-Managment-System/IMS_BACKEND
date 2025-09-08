from django.contrib import admin

from inspection_management.models import *

admin.site.register(Company)
admin.site.register(DataGroup)
admin.site.register(Site)
admin.site.register(BusinessUnit)
admin.site.register(AnalysisType)
admin.site.register(Equipment)
admin.site.register(Facility)
admin.site.register(InspectionAnalysis)
admin.site.register(Location)
admin.site.register(Parameter)
admin.site.register(Suite)
admin.site.register(Unit)
admin.site.register(InspectionPoint)
admin.site.register(InspectionTest)
admin.site.register(InspectionResult)
admin.site.register(Evince)
admin.site.register(Planner)
admin.site.register(EquipmentType)
admin.site.register(DataList)

# HSE Workflow Models Admin
@admin.register(HSEObservation)
class HSEObservationAdmin(admin.ModelAdmin):
    list_display = ['title', 'risk_level', 'workflow_state', 'created_by', 'created_at']
    list_filter = ['risk_level', 'workflow_state', 'affected_department']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(HSEWorkflowHistory)
class HSEWorkflowHistoryAdmin(admin.ModelAdmin):
    list_display = ['observation', 'from_state', 'to_state', 'action_by', 'created_at']
    list_filter = ['from_state', 'to_state']
    readonly_fields = ['created_at']

@admin.register(HSEEvidence)
class HSEEvidenceAdmin(admin.ModelAdmin):
    list_display = ['observation', 'file_name', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type']
    readonly_fields = ['uploaded_at']
