from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..viewsets.hse_viewsets import (
    HSEEnvironmentalDataViewSet,
    HSESafetyIncidentViewSet,
    HSEEquipmentViewSet,
    HSEComplianceViewSet,
    HSETrainingViewSet,
    HSEReportsViewSet,
    HSEAlertsViewSet
)

router = DefaultRouter()
router.register(r'environmental-data', HSEEnvironmentalDataViewSet, basename='hse-environmental-data')
router.register(r'safety-incidents', HSESafetyIncidentViewSet, basename='hse-safety-incidents')
router.register(r'equipment', HSEEquipmentViewSet, basename='hse-equipment')
router.register(r'compliance', HSEComplianceViewSet, basename='hse-compliance')
router.register(r'training', HSETrainingViewSet, basename='hse-training')
router.register(r'reports', HSEReportsViewSet, basename='hse-reports')
router.register(r'alerts', HSEAlertsViewSet, basename='hse-alerts')

urlpatterns = [
    path('hse/', include(router.urls)),
] 