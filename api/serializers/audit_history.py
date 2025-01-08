from rest_framework import serializers

from users.models.audit_history import AuditHistory


class AuditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditHistory
        fields = "__all__"
