from rest_framework import serializers

from inspection_management.models import InspectionResult


class SimplifiedInspectionResultSerializer(serializers.ModelSerializer):
    inspection_analysis = serializers.SerializerMethodField()
    parameter_name = serializers.SerializerMethodField()
    min_value = serializers.SerializerMethodField()
    max_value = serializers.SerializerMethodField()
    avg_value = serializers.SerializerMethodField()
    string_value = serializers.SerializerMethodField()
    checklist_data_type = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = InspectionResult
        fields = [
            "inspection_analysis",
            "parameter_name",
            "status",
            "min_value",
            "max_value",
            "avg_value",
            "string_value",
            "checklist_data_type",
            "entered_value",
            "comments",
            "id",
            "attachment_name",
            "attachment",
            "sample_required",
            "sample_content",
        ]

    def get_inspection_analysis(self, obj):

        return obj.inspection_test.inspection_analysis.name

    def get_parameter_name(self, obj):
        if obj.inspection_test.inspection_analysis.parameter_set.first():
            return obj.inspection_test.inspection_analysis.parameter_set.first().name
        return obj.inspection_test.inspection_analysis.name

    def get_min_value(self, obj):
        if obj.inspection_test.inspection_analysis.parameter_set.first():
            return (
                obj.inspection_test.inspection_analysis.parameter_set.first().min_value
            )

    def get_max_value(self, obj):
        if obj.inspection_test.inspection_analysis.parameter_set.first():
            return (
                obj.inspection_test.inspection_analysis.parameter_set.first().max_value
            )

    def get_avg_value(self, obj):
        if obj.inspection_test.inspection_analysis.parameter_set.first():
            return (
                obj.inspection_test.inspection_analysis.parameter_set.first().avg_value
            )

    def get_string_value(self, obj):
        if obj.inspection_test.inspection_analysis.parameter_set.first():
            return (
                obj.inspection_test.inspection_analysis.parameter_set.first().string_value
            )

    def get_checklist_data_type(self, obj):
        if obj.inspection_test.inspection_analysis.parameter_set.first():
            return (
                obj.inspection_test.inspection_analysis.parameter_set.first().checklist_data_type
            )

    def get_attachment_name(self, obj):
        if obj.attachment_name:
            return obj.attachment_name

    def get_attachment(self, obj):
        if obj.attachment:
            return obj.attachment
