
from api.services.detailed_entity_records import get_model_counts
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class AdminChartsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="detailed_entity_records")
    def fetch_detailed_records(self, request):
        data = get_model_counts()
        return Response(data)

    @action(detail=False, methods=["get"], url_path="another_function")
    def another_function(self, request):
        data = {"message": "Another function called."}
        return Response(data)
