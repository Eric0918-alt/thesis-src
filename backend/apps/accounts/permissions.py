from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import User


class IsAdminRole(BasePermission):
    message = "仅管理员可执行此操作"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.ROLE_ADMIN
        )


class IsAdminOrTeacherReadOnly(BasePermission):
    message = "您没有权限访问此资源"

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == User.ROLE_ADMIN:
            return True
        if request.user.role == User.ROLE_TEACHER and request.method in SAFE_METHODS:
            return True
        return False


class IsAdminOrReadOnlyForAuth(BasePermission):
    message = "仅管理员可执行修改操作"

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == User.ROLE_ADMIN
