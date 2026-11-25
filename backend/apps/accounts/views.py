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
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminOrTeacherReadOnly, IsAdminRole
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    StudentManageSerializer,
    StudentRegisterSerializer,
    TeacherManageSerializer,
    TeacherRegisterSerializer,
    UserProfileSerializer,
)
from apps.audit.models import SystemLog
from apps.audit.utils import record_log


def _read_tabular_file(uploaded_file) -> pd.DataFrame:
    filename = (uploaded_file.name or "").lower()
    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file, dtype=str).fillna("")
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(uploaded_file, dtype=str, engine="openpyxl").fillna("")
    raise ValueError("仅支持 .xlsx 或 .csv 格式文件")


def _export_dataframe(df: pd.DataFrame, sheet_name: str, download_name: str) -> HttpResponse:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buf.seek(0)
    filename = quote(download_name)
    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"
    return response


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            record_log(
                request,
                module="认证登录",
                action="用户登录",
                detail=f"登录失败：{serializer.errors}",
                status=SystemLog.STATUS_FAILED,
                username=str(request.data.get("username", "")),
                role=str(request.data.get("role", "")),
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        record_log(
            request,
            module="认证登录",
            action="用户登录",
            detail=f"用户 {user.username}（{user.get_role_display()}）登录系统",
            username=user.username,
            role=user.role,
        )
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserProfileSerializer(user).data,
            }
        )


class StudentRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        record_log(
            request,
            module="认证登录",
            action="学生注册",
            detail=f"新学生注册：{user.username}（{user.real_name}，{user.cohort}）",
            username=user.username,
            role=user.role,
        )
        return Response(
            {"detail": "注册成功", "user": UserProfileSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class TeacherRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TeacherRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        record_log(
            request,
            module="认证登录",
            action="教师注册",
            detail=f"新教师注册：{user.username}（{user.real_name}）",
            username=user.username,
            role=user.role,
        )
        return Response(
            {"detail": "注册成功", "user": UserProfileSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        record_log(
            request,
            module="个人中心",
            action="修改个人信息",
            detail=f"更新个人信息：{user.username}（{user.real_name}）",
        )
        return Response(UserProfileSerializer(user).data)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        record_log(
            request,
            module="个人中心",
            action="修改密码",
            detail=f"用户 {request.user.username} 修改了登录密码",
        )
        return Response({"detail": "密码修改成功"})


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentManageSerializer
    permission_classes = [IsAdminOrTeacherReadOnly]
    ordering_fields = ["id", "username", "real_name", "cohort", "gender", "phone", "date_joined"]
    ordering = ["-id"]

    def get_queryset(self):
        qs = User.objects.filter(role=User.ROLE_STUDENT)
        student_no = self.request.query_params.get("student_no", "").strip()
        student_name = self.request.query_params.get("student_name", "").strip()
        cohort = self.request.query_params.get("cohort", "").strip()
        if student_no:
            qs = qs.filter(username__icontains=student_no)
        if student_name:
            qs = qs.filter(real_name__icontains=student_name)
        if cohort:
            qs = qs.filter(cohort__icontains=cohort)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        record_log(self.request, "学生管理", "新增学生", f"新增学生 {obj.username}（{obj.real_name}）")

    def perform_update(self, serializer):
        obj = serializer.save()
        record_log(self.request, "学生管理", "编辑学生", f"编辑学生 {obj.username}（{obj.real_name}）")

    def perform_destroy(self, instance):
        info = f"{instance.username}（{instance.real_name}）"
        instance.delete()
        record_log(self.request, "学生管理", "删除学生", f"删除学生 {info}")

    @action(detail=False, methods=["post"], url_path="batch-delete", permission_classes=[IsAdminRole])
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list) or not ids:
            return Response({"detail": "请选择要删除的学生"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = User.objects.filter(role=User.ROLE_STUDENT, id__in=ids).delete()
        record_log(request, "学生管理", "批量删除", f"批量删除 {deleted_count} 名学生")
        return Response({"deleted": deleted_count})

    @action(detail=False, methods=["get"], url_path="template", permission_classes=[IsAdminRole])
    def download_template(self, request):
        df = pd.DataFrame(
            [{"学生学号": "2023001", "学生姓名": "示例学生", "届别": "2023届", "性别": "男", "手机": "13800000001", "初始密码": "123456"}]
        )
        return _export_dataframe(df, "学生导入模板", "学生导入模板.xlsx")

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
            return Response({"detail": "请上传 Excel 或 CSV 文件"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            df = _read_tabular_file(file_obj)
        except Exception as exc:
            return Response({"detail": f"文件解析失败：{exc}"}, status=status.HTTP_400_BAD_REQUEST)

        required_cols = ["学生学号", "学生姓名", "届别", "性别", "手机"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            return Response(
                {"detail": f"缺少必填列：{', '.join(missing_cols)}", "errors": []},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = []
        seen_nos = set()
        existing_nos = set(User.objects.values_list("username", flat=True))
        to_create = []

        for idx, row in df.iterrows():
            row_num = int(idx) + 2
            s_no = str(row["学生学号"]).strip()
            s_name = str(row["学生姓名"]).strip()
            cohort = str(row["届别"]).strip()
            gender = str(row["性别"]).strip()
            phone = str(row["手机"]).strip()
            pwd = str(row["初始密码"]).strip() if "初始密码" in df.columns and str(row["初始密码"]).strip() else "123456"

            if not s_no:
                errors.append({"row": row_num, "field": "学生学号", "reason": "学生学号不能为空"})
            elif s_no in seen_nos:
                errors.append({"row": row_num, "field": "学生学号", "reason": f"文件内学号 {s_no} 重复"})
            elif s_no in existing_nos:
                errors.append({"row": row_num, "field": "学生学号", "reason": f"学号 {s_no} 已存在"})
            if not s_name:
                errors.append({"row": row_num, "field": "学生姓名", "reason": "学生姓名不能为空"})
            if not cohort:
                errors.append({"row": row_num, "field": "届别", "reason": "届别不能为空"})
            if gender not in ("男", "女"):
                errors.append({"row": row_num, "field": "性别", "reason": "性别必须为“男”或“女”"})
            if not phone:
                errors.append({"row": row_num, "field": "手机", "reason": "手机不能为空"})

            seen_nos.add(s_no)
            to_create.append((s_no, s_name, cohort, gender, phone, pwd))

        if errors:
            record_log(request, "学生管理", "批量导入", f"校验失败，共 {len(errors)} 处错误", status=SystemLog.STATUS_FAILED)
            return Response({"detail": "导入数据校验未通过，请修正后重新导入", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for s_no, s_name, cohort, gender, phone, pwd in to_create:
                User.objects.create_user(
                    username=s_no,
                    password=pwd,
                    role=User.ROLE_STUDENT,
                    real_name=s_name,
                    cohort=cohort,
                    gender=gender,
                    phone=phone,
                )

        record_log(request, "学生管理", "批量导入", f"成功导入 {len(to_create)} 名学生")
        return Response({"imported": len(to_create), "detail": f"成功导入 {len(to_create)} 条学生记录"})

    @action(detail=False, methods=["get"], url_path="export", permission_classes=[IsAdminRole])
    def export_excel(self, request):
        ids_param = request.query_params.get("ids", "").strip()
        qs = self.get_queryset()
        if ids_param:
            id_list = [int(x) for x in ids_param.split(",") if x.strip().isdigit()]
            qs = qs.filter(id__in=id_list)
        rows = [
            {
                "学生学号": item.username,
                "学生姓名": item.real_name,
                "届别": item.cohort,
                "性别": item.gender,
                "手机": item.phone,
            }
            for item in qs
        ]
        df = pd.DataFrame(rows, columns=["学生学号", "学生姓名", "届别", "性别", "手机"])
        record_log(request, "学生管理", "导出数据", f"导出 {len(rows)} 条学生记录")
        return _export_dataframe(df, "学生列表", "学生列表.xlsx")


class TeacherViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherManageSerializer
    permission_classes = [IsAdminRole]
    ordering_fields = ["id", "username", "real_name", "gender", "phone", "date_joined"]
    ordering = ["-id"]

    def get_queryset(self):
        qs = User.objects.filter(role=User.ROLE_TEACHER)
        teacher_no = self.request.query_params.get("teacher_no", "").strip()
        teacher_name = self.request.query_params.get("teacher_name", "").strip()
        if teacher_no:
            qs = qs.filter(username__icontains=teacher_no)
        if teacher_name:
            qs = qs.filter(real_name__icontains=teacher_name)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        record_log(self.request, "教师管理", "新增教师", f"新增教师 {obj.username}（{obj.real_name}）")

    def perform_update(self, serializer):
        obj = serializer.save()
        record_log(self.request, "教师管理", "编辑教师", f"编辑教师 {obj.username}（{obj.real_name}）")

    def perform_destroy(self, instance):
        info = f"{instance.username}（{instance.real_name}）"
        instance.delete()
        record_log(self.request, "教师管理", "删除教师", f"删除教师 {info}")

    @action(detail=False, methods=["post"], url_path="batch-delete")
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list) or not ids:
            return Response({"detail": "请选择要删除的教师"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = User.objects.filter(role=User.ROLE_TEACHER, id__in=ids).delete()
        record_log(request, "教师管理", "批量删除", f"批量删除 {deleted_count} 名教师")
        return Response({"deleted": deleted_count})

    @action(detail=False, methods=["get"], url_path="template")
    def download_template(self, request):
        df = pd.DataFrame(
            [{"教师工号": "T101", "教师姓名": "示例教师", "性别": "女", "手机号码": "13900000001", "初始密码": "123456"}]
        )
        return _export_dataframe(df, "教师导入模板", "教师导入模板.xlsx")

    @action(
        detail=False,
        methods=["post"],
        url_path="import",
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_excel(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "请上传 Excel 或 CSV 文件"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            df = _read_tabular_file(file_obj)
        except Exception as exc:
            return Response({"detail": f"文件解析失败：{exc}"}, status=status.HTTP_400_BAD_REQUEST)

        required_cols = ["教师工号", "教师姓名"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            return Response(
                {"detail": f"缺少必填列：{', '.join(missing_cols)}", "errors": []},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = []
        seen_nos = set()
        existing_nos = set(User.objects.values_list("username", flat=True))
        to_create = []

        for idx, row in df.iterrows():
            row_num = int(idx) + 2
            t_no = str(row["教师工号"]).strip()
            t_name = str(row["教师姓名"]).strip()
            gender = str(row["性别"]).strip() if "性别" in df.columns else ""
            phone = str(row["手机号码"]).strip() if "手机号码" in df.columns else ""
            pwd = str(row["初始密码"]).strip() if "初始密码" in df.columns and str(row["初始密码"]).strip() else "123456"

            if not t_no:
                errors.append({"row": row_num, "field": "教师工号", "reason": "教师工号不能为空"})
            elif t_no in seen_nos:
                errors.append({"row": row_num, "field": "教师工号", "reason": f"文件内工号 {t_no} 重复"})
            elif t_no in existing_nos:
                errors.append({"row": row_num, "field": "教师工号", "reason": f"工号 {t_no} 已存在"})
            if not t_name:
                errors.append({"row": row_num, "field": "教师姓名", "reason": "教师姓名不能为空"})
            if gender and gender not in ("男", "女"):
                errors.append({"row": row_num, "field": "性别", "reason": "性别必须为空、“男”或“女”"})

            seen_nos.add(t_no)
            to_create.append((t_no, t_name, gender, phone, pwd))

        if errors:
            record_log(request, "教师管理", "批量导入", f"校验失败，共 {len(errors)} 处错误", status=SystemLog.STATUS_FAILED)
            return Response({"detail": "导入数据校验未通过，请修正后重新导入", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for t_no, t_name, gender, phone, pwd in to_create:
                User.objects.create_user(
                    username=t_no,
                    password=pwd,
                    role=User.ROLE_TEACHER,
                    real_name=t_name,
                    gender=gender,
                    phone=phone,
                )

        record_log(request, "教师管理", "批量导入", f"成功导入 {len(to_create)} 名教师")
        return Response({"imported": len(to_create), "detail": f"成功导入 {len(to_create)} 条教师记录"})

    @action(detail=False, methods=["get"], url_path="export")
    def export_excel(self, request):
        ids_param = request.query_params.get("ids", "").strip()
        qs = self.get_queryset()
        if ids_param:
            id_list = [int(x) for x in ids_param.split(",") if x.strip().isdigit()]
            qs = qs.filter(id__in=id_list)
        rows = [
            {
                "教师工号": item.username,
                "教师姓名": item.real_name,
                "性别": item.gender,
                "手机号码": item.phone,
            }
            for item in qs
        ]
        df = pd.DataFrame(rows, columns=["教师工号", "教师姓名", "性别", "手机号码"])
        record_log(request, "教师管理", "导出数据", f"导出 {len(rows)} 条教师记录")
        return _export_dataframe(df, "教师列表", "教师列表.xlsx")
