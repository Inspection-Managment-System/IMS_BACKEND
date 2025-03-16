from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ims_backend.utils.emirates_id_reader_automation import (
    format_raw_text, get_clipboard_data, open_glass_reader)
from users.authorization import role_required


User = get_user_model()


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class ReadEmiratesId(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        open_glass_reader()
        raw_data = get_clipboard_data()
        if raw_data:
            data = format_raw_text(raw_data)
        else:
            data = {"error": "No data found in clipboard"}

        if data == []:
            return Response(
                {
                    "message": "Please ensure that card reader is installed and connected properly."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(data, status=status.HTTP_200_OK)
