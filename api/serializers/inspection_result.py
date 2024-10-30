from rest_framework import serializers

from api.serializers import EvinceSerializer as ES
from api.serializers import InspectionTestSerializer as ITS
from api.serializers import RelatedFieldSerializer
from inspection_management.models import (Evince, InspectionResult,
                                          InspectionTest)


class SimplifiedInspectionResultSerializer(serializers.ModelSerializer):
    inspection_analysis = serializers.SerializerMethodField()
    min_value = serializers.SerializerMethodField()
    max_value = serializers.SerializerMethodField()
    avg_value = serializers.SerializerMethodField()
    string_value = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = InspectionResult
        fields = [
            "inspection_analysis",
            "status",
            "min_value",
            "max_value",
            "avg_value",
            "string_value",
            "entered_value",
            "comments",
            "id",
            "attachment_name",
            "attachment",
        ]

    def get_inspection_analysis(self, obj):

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

    def get_attachment_name(self, obj):
        if obj.attachment_name:
            return obj.attachment_name

    def get_attachment(self, obj):
        if obj.attachment:
            return obj.attachment
