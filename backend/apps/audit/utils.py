from __future__ import annotations

from typing import Optional

from apps.audit.models import SystemLog

ROLE_LABEL_MAP = {
    "student": "学生",
    "teacher": "教师",
    "admin": "管理员",
}


def get_client_ip(request) -> str:
    if request is None:
        return ""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def record_log(
    request,
    module: str,
    action: str,
    detail: str = "",
    status: str = SystemLog.STATUS_SUCCESS,
    username: Optional[str] = None,
    role: Optional[str] = None,
) -> None:
    try:
        user = getattr(request, "user", None)
        if username is None:
            if user is not None and getattr(user, "is_authenticated", False):
                username = user.username
            else:
                username = "匿名用户"
        if role is None:
            if user is not None and getattr(user, "is_authenticated", False):
                role = ROLE_LABEL_MAP.get(getattr(user, "role", ""), getattr(user, "role", ""))
            else:
                role = ""
        else:
            role = ROLE_LABEL_MAP.get(role, role)

        SystemLog.objects.create(
            username=username,
            role=role,
            module=module,
            action=action,
            method=getattr(request, "method", "SYSTEM") if request else "SYSTEM",
            path=getattr(request, "path", "") if request else "",
            detail=detail,
            ip_address=get_client_ip(request),
            status=status,
        )
    except Exception:
        # Logging must never break business transactions
        pass
