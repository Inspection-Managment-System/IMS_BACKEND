from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.viewsets import (
    BusinessUnitViewSet,
    CompanyViewSet,
    DatagroupViewSet,
    InspectionPointViewSet,
    LocationViewSet,
    SiteViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"datagroups", DatagroupViewSet, basename="datagroup")
router.register(r"users", UserViewSet, basename="user")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"sites", SiteViewSet, basename="site")
router.register(r"business_units", BusinessUnitViewSet, basename="business_unit")
router.register(
    r"inspection_points", InspectionPointViewSet, basename="inspection_point"
)
router.register(r"locations", LocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("api.urls.user")),
]
