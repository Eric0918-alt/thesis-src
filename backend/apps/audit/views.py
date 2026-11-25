from __future__ import annotations

import io
from urllib.parse import quote

import pandas as pd
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminRole
from apps.audit.models import SystemLog


class SystemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = [
            "id",
            "username",
            "role",
            "module",
            "action",
            "method",
            "path",
            "detail",
            "ip_address",
            "status",
            "created_at",
        ]


class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SystemLogSerializer
    permission_classes = [IsAdminRole]
    ordering_fields = ["id", "username", "module", "status", "created_at"]
    ordering = ["-created_at", "-id"]

    def get_queryset(self):
        qs = SystemLog.objects.all()
        username = self.request.query_params.get("username", "").strip()
        module = self.request.query_params.get("module", "").strip()
        log_status = self.request.query_params.get("status", "").strip()
        keyword = self.request.query_params.get("keyword", "").strip()

        if username:
            qs = qs.filter(username__icontains=username)
        if module:
            qs = qs.filter(module__icontains=module)
        if log_status:
            qs = qs.filter(status=log_status)
        if keyword:
            qs = qs.filter(Q(action__icontains=keyword) | Q(detail__icontains=keyword))
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="batch-delete")
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list) or not ids:
            return Response({"detail": "请选择要删除的日志记录"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = SystemLog.objects.filter(id__in=ids).delete()
        return Response({"deleted": deleted_count})

    @action(detail=False, methods=["get"], url_path="export")
    def export_excel(self, request):
        ids_param = request.query_params.get("ids", "").strip()
        qs = self.get_queryset()
        if ids_param:
            id_list = [int(x) for x in ids_param.split(",") if x.strip().isdigit()]
            qs = qs.filter(id__in=id_list)

        rows = [
            {
                "操作用户": item.username,
                "用户角色": item.role,
                "操作模块": item.module,
                "操作类型": item.action,
                "请求方法": item.method,
                "请求路径": item.path,
                "操作详情": item.detail,
                "IP地址": item.ip_address,
                "状态": item.status,
                "操作时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for item in qs
        ]
        df = pd.DataFrame(
            rows,
            columns=["操作用户", "用户角色", "操作模块", "操作类型", "请求方法", "请求路径", "操作详情", "IP地址", "状态", "操作时间"],
        )
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="系统日志")
        buf.seek(0)

        filename = quote("系统日志.xlsx")
        response = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"
        return response
