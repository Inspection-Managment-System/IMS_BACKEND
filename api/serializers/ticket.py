from rest_framework import serializers

from inspection_management.models import Ticket


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ('opened_by',)