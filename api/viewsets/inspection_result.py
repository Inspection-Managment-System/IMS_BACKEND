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
        print(f"=== DEBUG: Updating inspection result {pk} ===")
        print(f"Request data: {request.data}")
        
        inspection_result = get_object_or_404(InspectionResult, pk=pk)
        print(f"Found inspection result: {inspection_result.id}, evince: {inspection_result.evince.id}")
        
        entered_value = request.data.get("entered_value", None)
        comments = request.data.get("comments", "")
        attachment_name = request.data.get("attachment_name", "")
        attachment = request.data.get("attachment", "")
        sample_required = request.data.get("sample_required", False)
        
        print(f"entered_value: '{entered_value}', comments: '{comments}'")
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

        # Check if the entered value is out of spec
        inspection_result.is_out_of_spec = False
        if entered_value and inspection_result.inspection_test.inspection_analysis.parameter_set.exists():
            parameter = inspection_result.inspection_test.inspection_analysis.parameter_set.first()
            
            # Check numeric parameters (with min/max values)
            if parameter.min_value is not None and parameter.max_value is not None:
                try:
                    numeric_value = float(entered_value)
                    if numeric_value < parameter.min_value or numeric_value > parameter.max_value:
                        inspection_result.is_out_of_spec = True
                except (ValueError, TypeError):
                    # If it's not a numeric value, skip numeric check
                    pass
            
            # Check boolean/string parameters (with checklist_data_type and string_value)
            elif parameter.checklist_data_type and parameter.string_value:
                entered_lower = str(entered_value).strip().upper()
                expected_lower = str(parameter.string_value).strip().upper()
                
                # For YES/NO, TRUE/FALSE, Satisfactory/Unsatisfactory parameters
                # If entered value doesn't match expected value, it's out of spec
                if entered_lower != expected_lower:
                    inspection_result.is_out_of_spec = True
                    print(f"Out-of-spec detected for {parameter.name}: entered '{entered_value}' != expected '{parameter.string_value}'")

        if attachment and attachment_name:
            inspection_result.attachment_name = attachment_name
            inspection_result.attachment = attachment

        inspection_result.save()
        print(f"Saved inspection result: entered_value='{inspection_result.entered_value}', status='{inspection_result.status}'")

        return Response(
            {"message": "Inspection result updated successfully."},
            status=status.HTTP_200_OK,
        )
