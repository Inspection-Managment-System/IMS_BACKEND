from rest_framework import serializers
from .user import UserSerializer
from inspection_management.models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    opened_by = UserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ('opened_by',)