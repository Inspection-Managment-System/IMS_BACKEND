from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SimplifiedInspectionResultSerializer
from inspection_management.models import InspectionResult


class InspectionResultViewSet(viewsets.ModelViewSet):
    queryset = InspectionResult.objects.all()
    serializer_class = SimplifiedInspectionResultSerializer

    @action(detail=True, methods=["post"], url_path="update")
    def update_inspection(self, request, pk=None):
        """
        Allows the user to update the entered_value and optional comments,
        and marks the status as 'Completed'.
        """
        inspection_result = get_object_or_404(InspectionResult, pk=pk)
        entered_value = request.data.get("entered_value", None)
        comments = request.data.get("comments", "")
        attachment_name = request.data.get("attachment_name", "")
        attachment = request.data.get("attachment", "")
        sample_required = request.data.get("sample_required", False)
        if sample_required:
            inspection_result.sample_required = True
            inspection_result.sample_content = request.data.get("sample_content", None)
        else:
            inspection_result.sample_required = False
            inspection_result.sample_content = None

        if not entered_value:
            return Response(
                {"error": "Entered value is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        inspection_result.entered_value = entered_value
        inspection_result.comments = comments
        inspection_result.status = "Completed"

        if attachment and attachment_name:
            inspection_result.attachment_name = attachment_name
            inspection_result.attachment = attachment

        inspection_result.save()

        return Response(
            {"message": "Inspection result updated successfully."},
            status=status.HTTP_200_OK,
        )
