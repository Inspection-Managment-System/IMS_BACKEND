from rest_framework import serializers

from api.serializers import RelatedFieldSerializer
from api.serializers.user import UserSerializer
from users.models.audit_history import AuditHistory


class AuditHistorySerializer(serializers.ModelSerializer):
    user = RelatedFieldSerializer(
        queryset=UserSerializer.Meta.model.objects.all(), serializer=UserSerializer
    )

    class Meta:
        model = AuditHistory
        fields = "__all__"
