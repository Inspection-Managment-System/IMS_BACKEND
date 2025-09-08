from rest_framework import serializers
from inspection_management.models.hse_result import HSEResult
from api.serializers import UserSerializer as US


class HSEResultSerializer(serializers.ModelSerializer):
    entered_by = US(read_only=True)
    
    class Meta:
        model = HSEResult
        fields = '__all__'
        read_only_fields = ['entered_by', 'entered_at']
    
    def create(self, validated_data):
        # Set the entered_by field from the request user
        validated_data['entered_by'] = self.context['request'].user
        return super().create(validated_data)
