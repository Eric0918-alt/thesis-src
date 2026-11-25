from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.audit.views import SystemLogViewSet

router = DefaultRouter()
router.register(r"logs", SystemLogViewSet, basename="system-log")

urlpatterns = [
    path("", include(router.urls)),
]
