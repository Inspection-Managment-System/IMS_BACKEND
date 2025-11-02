from django.urls import path
from api.viewsets.setup import SetupStatusView, SetupInitializeView

urlpatterns = [
    path('status/', SetupStatusView.as_view(), name='setup-status'),
    path('initialize/', SetupInitializeView.as_view(), name='setup-initialize'),
]

