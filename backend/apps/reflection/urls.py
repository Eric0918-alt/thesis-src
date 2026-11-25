from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.reflection.views import CodingResultViewSet, CohortViewSet

router = DefaultRouter()
router.register(r"cohorts", CohortViewSet, basename="cohort")
router.register(r"coding-results", CodingResultViewSet, basename="coding-result")

urlpatterns = [
    path("", include(router.urls)),
]
