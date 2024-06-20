from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.viewsets import DatagroupViewSet, UserViewSet

router = DefaultRouter()
router.register(r"datagroups", DatagroupViewSet)
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("api.urls.user")),
]
