from rest_framework import serializers

from inspection_management.models import Sample


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "SAMPLE_NUMBER",
            "TEXT_ID",
            "SAMPLE_VOLUME",
            "SAMPLE_UNITS",
            "SAMPLE_TYPE",
            "CONTAINER_TYPE",
        ]
        extra_kwargs = {
            "SAMPLE_NUMBER": {"validators": []},
        }
