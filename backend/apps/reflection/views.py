from __future__ import annotations

import io
from urllib.parse import quote

import pandas as pd
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminOrReadOnlyForAuth, IsAdminRole
from apps.audit.models import SystemLog
from apps.audit.utils import record_log
from apps.reflection.models import CodingResult, Cohort
from apps.reflection.serializers import CodingResultSerializer, CohortSerializer
from apps.reflection.validators import COLUMN_TO_FIELD, validate_coding_dataframe


def _export_excel(df: pd.DataFrame, sheet_name: str, filename: str) -> HttpResponse:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buf.seek(0)
    encoded_name = quote(filename)
    resp = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_name}"
    return resp


class CohortViewSet(viewsets.ModelViewSet):
    serializer_class = CohortSerializer
    ordering_fields = ["id", "name", "created_at"]
    ordering = ["id"]

    def get_permissions(self):
        if self.action in ("list", "retrieve", "all_options"):
            return [AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        qs = Cohort.objects.all()
        name = self.request.query_params.get("name", "").strip()
        if name:
            qs = qs.filter(name__icontains=name)
        return qs

    @action(detail=False, methods=["get"], url_path="all", permission_classes=[AllowAny])
    def all_options(self, request):
        data = CohortSerializer(Cohort.objects.all().order_by("name"), many=True).data
        return Response(data)

    def perform_create(self, serializer):
        obj = serializer.save()
        record_log(self.request, "届别管理", "新增届别", f"新增届别：{obj.name}")

    def perform_update(self, serializer):
        obj = serializer.save()
        record_log(self.request, "届别管理", "编辑届别", f"编辑届别：{obj.name}")

    def perform_destroy(self, instance):
        name = instance.name
        instance.delete()
        record_log(self.request, "届别管理", "删除届别", f"删除届别：{name}")

    @action(detail=False, methods=["post"], url_path="batch-delete", permission_classes=[IsAdminRole])
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list) or not ids:
            return Response({"detail": "请选择要删除的届别"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Cohort.objects.filter(id__in=ids).delete()
        record_log(request, "届别管理", "批量删除", f"批量删除 {deleted_count} 条届别记录")
        return Response({"deleted": deleted_count})


class CodingResultViewSet(viewsets.ModelViewSet):
    serializer_class = CodingResultSerializer
    permission_classes = [IsAdminOrReadOnlyForAuth]
    ordering_fields = [
        "id",
        "student_no",
        "article_no",
        "cohort",
        "segment_no",
        "segment_order",
        "source_row_no",
        "problem_description",
        "cause_analysis",
        "improvement_strategy",
        "effectiveness_eval",
        "description_level",
        "descriptive_reflection",
        "dialogic_reflection",
        "critical_reflection",
    ]
    ordering = ["-id"]

    def get_queryset(self):
        user = self.request.user
        qs = CodingResult.objects.all()

        # 学生角色严格隔离，仅可查看本人学号对应的编码结果
        if user.role == User.ROLE_STUDENT:
            qs = qs.filter(student_no=user.username)

        student_no = self.request.query_params.get("student_no", "").strip()
        article_no = self.request.query_params.get("article_no", "").strip()
        cohort = self.request.query_params.get("cohort", "").strip()

        if student_no:
            qs = qs.filter(student_no__icontains=student_no)
        if article_no:
            qs = qs.filter(article_no__icontains=article_no)
        if cohort:
            qs = qs.filter(cohort__icontains=cohort)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        if obj.cohort:
            Cohort.objects.get_or_create(name=obj.cohort)
        record_log(
            self.request,
            "编码结果",
            "新增记录",
            f"新增编码记录：{obj.student_no}-{obj.article_no}-{obj.segment_no}",
        )

    def perform_update(self, serializer):
        obj = serializer.save()
        if obj.cohort:
            Cohort.objects.get_or_create(name=obj.cohort)
        record_log(
            self.request,
            "编码结果",
            "编辑记录",
            f"编辑编码记录：{obj.student_no}-{obj.article_no}-{obj.segment_no}",
        )

    def perform_destroy(self, instance):
        key = f"{instance.student_no}-{instance.article_no}-{instance.segment_no}"
        instance.delete()
        record_log(self.request, "编码结果", "删除记录", f"删除编码记录：{key}")

    @action(detail=False, methods=["post"], url_path="batch-delete", permission_classes=[IsAdminRole])
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list) or not ids:
            return Response({"detail": "请选择要删除的编码结果"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = CodingResult.objects.filter(id__in=ids).delete()
        record_log(request, "编码结果", "批量删除", f"批量删除 {deleted_count} 条编码结果")
        return Response({"deleted": deleted_count})

    @action(detail=False, methods=["get"], url_path="template", permission_classes=[IsAuthenticated])
    def download_template(self, request):
        sample_rows = [
            {
                "学生学号": "2023001",
                "文章编号": "A2023001",
                "届别": "2023届",
                "片段编号": "S001",
                "片段顺序": 1,
                "来源表行号": 2,
                "问题描述": 1,
                "原因分析": 1,
                "改进策略": 0,
                "有效性评估": 0,
                "描述层": 0,
                "描述性反思": 1,
                "对话性反思": 0,
                "批判性反思": 0,
            }
        ]
        df = pd.DataFrame(sample_rows, columns=[col for col, _ in COLUMN_TO_FIELD])
        return _export_excel(df, "编码结果导入模板", "编码结果导入模板.xlsx")

    @action(
        detail=False,
        methods=["post"],
        url_path="import",
        permission_classes=[IsAdminRole],
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_excel(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "请上传 .xlsx 或 .csv 编码结果文件"}, status=status.HTTP_400_BAD_REQUEST)

        filename = (file_obj.name or "").lower()
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file_obj, dtype=str).fillna("")
            elif filename.endswith(".xlsx") or filename.endswith(".xls"):
                df = pd.read_excel(file_obj, dtype=str, engine="openpyxl").fillna("")
            else:
                return Response({"detail": "仅支持 .xlsx 或 .csv 文件格式"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            record_log(request, "编码结果", "批量导入", f"文件解析失败：{exc}", status=SystemLog.STATUS_FAILED)
            return Response({"detail": f"文件解析失败：{exc}"}, status=status.HTTP_400_BAD_REQUEST)

        valid_objects, errors = validate_coding_dataframe(df)
        if errors:
            record_log(
                request,
                "编码结果",
                "批量导入",
                f"文件 {file_obj.name} 校验失败，共发现 {len(errors)} 处错误",
                status=SystemLog.STATUS_FAILED,
            )
            return Response(
                {
                    "detail": f"编码文件校验未通过（共 {len(errors)} 处错误），请由数据提供方核实修正后重新导入",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            CodingResult.objects.bulk_create(valid_objects)
            for cohort_name in {obj.cohort for obj in valid_objects if obj.cohort}:
                Cohort.objects.get_or_create(name=cohort_name)

        record_log(
            request,
            "编码结果",
            "批量导入",
            f"从 {file_obj.name} 成功校验并导入 {len(valid_objects)} 条编码结果",
        )
        return Response(
            {
                "imported": len(valid_objects),
                "detail": f"校验通过，成功导入 {len(valid_objects)} 条编码结果",
            }
        )

    @action(detail=False, methods=["get"], url_path="export", permission_classes=[IsAdminRole])
    def export_excel(self, request):
        ids_param = request.query_params.get("ids", "").strip()
        qs = self.get_queryset()
        if ids_param:
            id_list = [int(x) for x in ids_param.split(",") if x.strip().isdigit()]
            qs = qs.filter(id__in=id_list)

        rows = [
            {col_name: getattr(item, field_name) for col_name, field_name in COLUMN_TO_FIELD}
            for item in qs
        ]
        df = pd.DataFrame(rows, columns=[col for col, _ in COLUMN_TO_FIELD])
        record_log(request, "编码结果", "导出数据", f"导出 {len(rows)} 条编码结果")
        return _export_excel(df, "编码结果", "编码结果.xlsx")
