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
        related_evince = inspection_result.inspection_test.evince

        if related_evince.evince_type == "Checklist":
            is_checked = request.data.get("is_checked")
            parameter = (
                inspection_result.inspection_test.inspection_analysis.parameter_set.first()
            )

            if parameter:
                parameter.is_checked = is_checked
                parameter.save()

        else:
            entered_value = request.data.get("entered_value")
            if not entered_value:
                return Response(
                    {"error": "Entered value is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            inspection_result.entered_value = entered_value
            inspection_result.comments = request.data.get("comments", "")

            if "attachment" in request.data and "attachment_name" in request.data:
                inspection_result.attachment_name = request.data["attachment_name"]
                inspection_result.attachment = request.data["attachment"]

        inspection_result.status = "Completed"

        inspection_result.save()

        return Response(
            {"message": "Inspection result updated successfully."},
            status=status.HTTP_200_OK,
        )
