# inspection_management/urls.py

from django.urls import path

from api.viewsets.admin_charts import AdminChartsView

urlpatterns = [
    path(
        "detailed_entity_records/",
        AdminChartsView.as_view(),
        name="fetch_detailed_records",
    ),
    path("another_function/", AdminChartsView.as_view(), name="another_function"),
]
