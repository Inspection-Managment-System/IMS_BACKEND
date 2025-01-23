from rest_framework import serializers

from api.serializers import RelatedFieldSerializer
from api.serializers.user import UserSerializer
from users.models.notification import Notification


class NotificationSerializer(serializers.ModelSerializer):
    recipient = RelatedFieldSerializer(
        queryset=UserSerializer.Meta.model.objects.all(), serializer=UserSerializer
    )
    sender = RelatedFieldSerializer(
        queryset=UserSerializer.Meta.model.objects.all(), serializer=UserSerializer
    )

    class Meta:
        model = Notification
        fields = "__all__"
