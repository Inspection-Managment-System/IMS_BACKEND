from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.viewsets import CompanyViewSet, DatagroupViewSet, UserViewSet

router = DefaultRouter()
router.register(r"datagroups", DatagroupViewSet)
router.register(r"users", UserViewSet)
router.register(r"company", CompanyViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("api.urls.user")),
]
