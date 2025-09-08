from django.db.models import Count
from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import InspectionAnalysisSerializer
from ims_backend.utils.helper import \
    get_related_inspection_analyses_from_analysis_type
from inspection_management.models import (AnalysisType, DataGroup, Equipment,
                                          InspectionAnalysis, Location)
from users.authorization import role_required
from users.models import User
from users.models.audit_history import AuditHistory
from users.models.notification import Notification


@method_decorator(role_required(allowed_roles=["Admin", "Manager", "Inspector"]), name="dispatch")
class InspectionAnalysisViewSet(viewsets.ModelViewSet):
    queryset = InspectionAnalysis.objects.all()
    serializer_class = InspectionAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        analysis_type_name = request.query_params.get("analysis_type", None)
        list_for_evince = request.query_params.get("list_for_evince", None)
        if analysis_type_name:
            related_inspection_analyses = (
                get_related_inspection_analyses_from_analysis_type(analysis_type_name)
            )
            self.queryset = related_inspection_analyses
        if list_for_evince:
            self.queryset = self.queryset.annotate(
                param_count=Count("parameter")
            ).filter(param_count__gt=0)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Only Admin can create inspection analyses
        if request.user.userprofile.role.name != "Admin":
            return Response(
                {"error": "Only Admin users can create inspection analyses"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Created inspection analysis: {serializer.instance.name}",
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )

    def update(self, request, *args, **kwargs):
        # Only Admin can update inspection analyses
        if request.user.userprofile.role.name != "Admin":
            return Response(
                {"error": "Only Admin users can update inspection analyses"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        data = request.data.copy()
        data = self.preprocess_data(data)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        original_name = instance.name

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        AuditHistory.objects.create(
            user=request.user,
            action=f"Updated inspection analysis: {original_name} → {serializer.instance.name}",
        )

        if original_name != serializer.instance.name:
            try:
                inspectors = User.objects.filter(userprofile__role__name="Inspector")

                if inspectors.exists():
                    for inspector in inspectors:
                        Notification.objects.create(
                            sender=request.user,
                            recipient=inspector,
                            content=f"Inspection analysis '{original_name}' has been renamed to '{serializer.instance.name}'.",
                        )
            except Exception as e:
                print(f"Error sending inspector notifications: {str(e)}")

        return Response(serializer.data)

    def perform_destroy(self, instance):
        analysis_name = instance.name

        AuditHistory.objects.create(
            user=self.request.user,
            action=f"Deleted inspection analysis: {analysis_name}",
        )

        instance.delete()

    def preprocess_data(self, data):
        if "name" in data:
            data["name"] = data["name"].lower()
        if "group" in data:
            group_name = data.get("group")
            data["group"] = DataGroup.objects.get(name=group_name).id
        if "equipment" in data and data.get("equipment") != "":
            equipment_name = data.get("equipment")
            data["equipment"] = Equipment.objects.get(name=equipment_name).id
        if "analysis_type" in data:
            analysis_type_name = data.get("analysis_type")
            data["analysis_type"] = AnalysisType.objects.get(name=analysis_type_name).id
        if "location" in data:
            location_name = data.get("location")
            data["location"] = Location.objects.get(name=location_name).id
        return data
