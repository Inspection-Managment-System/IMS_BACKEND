from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.viewsets import (
    BusinessUnitViewSet,
    CompanyViewSet,
    DatagroupViewSet,
    InspectionPointViewSet,
    LocationViewSet,
    EquipmentTypeViewSet,
    SiteViewSet,
    UserViewSet,
    EquipmentViewSet,
    DataListViewSet,
    AnalysisTypeViewSet,
    UnitViewSet,
    InspectionAnalysisViewSet,
    ParameterViewSet,
    EvinceViewSet,
    PlannerViewSet,
    InspectionResultViewSet,
    AdminChartsViewSet,
    InspectorDashboardViewSet,
    ManagerChartsViewSet,
    IMSReportViewSet,
    NotificationViewSet,
    AuditHistoryViewSet,
    TicketViewSet,
    DocumentViewSet,
    SampleViewSet,
)
from api.viewsets.hse_result import HSEResultViewSet
from api.viewsets.maintenance_result import MaintenanceResultViewSet
from api.viewsets.hse_risk_assessment import HSERiskAssessmentViewSet
from api.viewsets.hse_risk_assessment_result import HSERiskAssessmentResultViewSet
from api.viewsets.external_departments import ExternalDepartmentViewSet

router = DefaultRouter()
router.register(r"datagroups", DatagroupViewSet, basename="datagroup")
router.register(r"audit_history", AuditHistoryViewSet, basename="audit_history")
router.register(r"notifications", NotificationViewSet, basename="notifications")
router.register(r"users", UserViewSet, basename="user")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"sites", SiteViewSet, basename="site")
router.register(r"business_units", BusinessUnitViewSet, basename="business_unit")
router.register(
    r"inspection_points", InspectionPointViewSet, basename="inspection_point"
)
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"equipment_types", EquipmentTypeViewSet, basename="equipment_type")
router.register(r"equipments", EquipmentViewSet, basename="equipment")
router.register(r"datalists", DataListViewSet, basename="datalists")
router.register(r"analysis_types", AnalysisTypeViewSet, basename="analysis_types")
router.register(r"units", UnitViewSet, basename="units")
router.register(
    r"inspection_analyses", InspectionAnalysisViewSet, basename="inspection_analyses"
)
router.register(r"parameters", ParameterViewSet, basename="parameters")
router.register(r"evinces", EvinceViewSet, basename="evinces")
router.register(r"planners", PlannerViewSet, basename="planners")
router.register(
    r"inspection_results", InspectionResultViewSet, basename="inspection_results"
)
router.register(r"hse_results", HSEResultViewSet, basename="hse_results")
router.register(r"maintenance_results", MaintenanceResultViewSet, basename="maintenance_results")
router.register(r"hse_risk_assessments", HSERiskAssessmentViewSet, basename="hse_risk_assessments")
router.register(r"hse_risk_assessment_results", HSERiskAssessmentResultViewSet, basename="hse_risk_assessment_results")
router.register(r"external_departments", ExternalDepartmentViewSet, basename="external_departments")
router.register(r"admin_charts", AdminChartsViewSet, basename="admin_charts")
router.register(
    r"inspector_dashboard", InspectorDashboardViewSet, basename="inspector_dashboard"
)

router.register(
    r"manager_dashboard", ManagerChartsViewSet, basename="manager_dashboard"
)

router.register(r"reports", IMSReportViewSet, basename="reports")
router.register(r"tickets", TicketViewSet, basename="tickets")
router.register(r"documents", DocumentViewSet, basename="documents")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("api.urls.user")),
    path("samples/", SampleViewSet.as_view()),
    path("", include("api.urls.hse")),
    path("setup/", include("api.urls.setup")),
]
