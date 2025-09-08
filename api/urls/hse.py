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
from ..viewsets.hse_workflow_viewsets import (
    HSEObservationViewSet,
    HSEWorkflowHistoryViewSet,
    HSEEvidenceViewSet
)

router = DefaultRouter()
router.register(r'environmental-data', HSEEnvironmentalDataViewSet, basename='hse-environmental-data')
router.register(r'safety-incidents', HSESafetyIncidentViewSet, basename='hse-safety-incidents')
router.register(r'equipment', HSEEquipmentViewSet, basename='hse-equipment')
router.register(r'compliance', HSEComplianceViewSet, basename='hse-compliance')
router.register(r'training', HSETrainingViewSet, basename='hse-training')
router.register(r'reports', HSEReportsViewSet, basename='hse-reports')
router.register(r'alerts', HSEAlertsViewSet, basename='hse-alerts')

# HSE Workflow URLs
router.register(r'observations', HSEObservationViewSet, basename='hse-observations')
router.register(r'workflow-history', HSEWorkflowHistoryViewSet, basename='hse-workflow-history')
router.register(r'evidence', HSEEvidenceViewSet, basename='hse-evidence')

urlpatterns = [
    path('hse/', include(router.urls)),
    # Add workflow-specific URLs
    path('hse/workflow/', include([
        path('dashboard-stats/', HSEObservationViewSet.as_view({'get': 'dashboard_stats'}), name='hse-workflow-dashboard-stats'),
        path('observations/', HSEObservationViewSet.as_view({'get': 'list', 'post': 'create'}), name='hse-workflow-observations'),
        path('observations/<int:pk>/', HSEObservationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='hse-workflow-observation-detail'),
        path('observations/<int:pk>/status/', HSEObservationViewSet.as_view({'patch': 'update_status'}), name='hse-workflow-observation-status'),
        path('observations/<int:pk>/assign/', HSEObservationViewSet.as_view({'patch': 'assign'}), name='hse-workflow-observation-assign'),
        path('history/', HSEWorkflowHistoryViewSet.as_view({'get': 'list'}), name='hse-workflow-history'),
        path('risk-levels/', HSEObservationViewSet.as_view({'get': 'risk_levels'}), name='hse-workflow-risk-levels'),
        path('categories/', HSEObservationViewSet.as_view({'get': 'categories'}), name='hse-workflow-categories'),
        path('workflow-states/', HSEObservationViewSet.as_view({'get': 'workflow_states'}), name='hse-workflow-states'),
        path('available-users/', HSEObservationViewSet.as_view({'get': 'available_users'}), name='hse-workflow-available-users'),
    ])),
] 