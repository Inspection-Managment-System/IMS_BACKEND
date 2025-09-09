from rest_framework import serializers
from inspection_management.models.maintenance_result import MaintenanceResult


class MaintenanceResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceResult
        fields = '__all__'
        read_only_fields = ['entered_by', 'entered_at']
    
    def create(self, validated_data):
        # Set the entered_by field from the request user
        validated_data['entered_by'] = self.context['request'].user
        return super().create(validated_data)
