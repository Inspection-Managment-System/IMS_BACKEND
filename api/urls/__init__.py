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
)

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
router.register(r"admin_charts", AdminChartsViewSet, basename="admin_charts")
router.register(
    r"inspector_dashboard", InspectorDashboardViewSet, basename="inspector_dashboard"
)

router.register(
    r"manager_dashboard", ManagerChartsViewSet, basename="manager_dashboard"
)

router.register(r"reports", IMSReportViewSet, basename="reports")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("api.urls.user")),
]
