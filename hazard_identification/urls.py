from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import HazardIdentificationViewSet, HazardCategoryViewSet, HazardUserViewSet

# Create router for API endpoints
router = DefaultRouter()
router.register(r'hazards', HazardIdentificationViewSet, basename='hazard')
router.register(r'categories', HazardCategoryViewSet, basename='hazard-category')
router.register(r'users', HazardUserViewSet, basename='hazard-user')

urlpatterns = [
    path('api/hazard_identification/', include(router.urls)),
]
