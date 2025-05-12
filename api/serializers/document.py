from rest_framework import serializers

from api.serializers import EquipmentSerializer as ES
from api.serializers import RelatedFieldSerializer
from api.serializers import SiteSerializer as SS
from api.serializers import UserSerializer as US
from inspection_management.models import Document, Equipment, Site
from users.models import User


class DocumentSerializer(serializers.ModelSerializer):
    site = RelatedFieldSerializer(queryset=Site.objects.all(), serializer=SS)
    equipment = RelatedFieldSerializer(queryset=Equipment.objects.all(), serializer=ES)
    uploaded_by = RelatedFieldSerializer(queryset=User.objects.all(), serializer=US)
    previous_version = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        view = self.context.get("view")
        if view and getattr(view, "action", None) == "list":
            data.pop("file", None)
        return data

    def get_previous_version(self, obj):
        if obj.previous_version:
            return DocumentSerializer(obj.previous_version, context=self.context).data
        return None
