from django.utils.decorators import method_decorator
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.serializers import InspectionPointSerializer
from inspection_management.models import BusinessUnit, InspectionPoint
from users.authorization import role_required


@method_decorator(role_required(allowed_roles=["Admin"]), name="dispatch")
class InspectionPointViewSet(viewsets.ModelViewSet):
    queryset = InspectionPoint.objects.all()
    serializer_class = InspectionPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data = self.preprocess_data(data)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def preprocess_data(self, data):

        if "name" in data:
            data["name"] = data["name"].lower()
        if "business_unit" in data:
            business_unit = BusinessUnit.objects.get(name=data.get("business_unit"))
            data["group"] = business_unit.group.id
            data["business_unit"] = business_unit.id

        return data
