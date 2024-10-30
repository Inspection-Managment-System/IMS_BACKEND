from django.http import JsonResponse
from django.views import View

from api.services.detailed_entity_records import get_model_counts


class AdminChartsView(View):
    def get(self, request, *args, **kwargs):
        if "detailed_entity_records" in request.path:
            return self.fetch_detailed_records(request, *args, **kwargs)
        else:
            return self.another_function(request, *args, **kwargs)

    def fetch_detailed_records(self, request, *args, **kwargs):
        data = get_model_counts()
        return JsonResponse(data)

    def another_function(self, request, *args, **kwargs):
        data = {"message": "Another function called."}
        return JsonResponse(data)
