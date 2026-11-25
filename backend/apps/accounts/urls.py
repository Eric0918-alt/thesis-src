from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    ChangePasswordAPIView,
    LoginAPIView,
    ProfileAPIView,
    StudentRegisterAPIView,
    StudentViewSet,
    TeacherRegisterAPIView,
    TeacherViewSet,
)

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="student")
router.register(r"teachers", TeacherViewSet, basename="teacher")

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/register/student/", StudentRegisterAPIView.as_view(), name="auth-register-student"),
    path("auth/register/teacher/", TeacherRegisterAPIView.as_view(), name="auth-register-teacher"),
    path("auth/profile/", ProfileAPIView.as_view(), name="auth-profile"),
    path("auth/change-password/", ChangePasswordAPIView.as_view(), name="auth-change-password"),
    path("", include(router.urls)),
]
