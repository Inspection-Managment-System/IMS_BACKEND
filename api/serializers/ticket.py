from rest_framework import serializers

from inspection_management.models import Ticket

from .user import UserSerializer


class TicketSerializer(serializers.ModelSerializer):
    opened_by = UserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ("opened_by",)
