from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.viewsets.risk_level import RiskLevelViewSet
from api.viewsets.risk_category import RiskCategoryViewSet
from api.viewsets.hse_observation_type import HSEObservationTypeViewSet

router = DefaultRouter()
router.register(r'risk-levels', RiskLevelViewSet, basename='risk-level')
router.register(r'risk-categories', RiskCategoryViewSet, basename='risk-category')
router.register(r'hse-observation-types', HSEObservationTypeViewSet, basename='hse-observation-type')

urlpatterns = [
    path('', include(router.urls)),
]

