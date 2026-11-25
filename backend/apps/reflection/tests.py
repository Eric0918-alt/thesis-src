from __future__ import annotations

import io

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.audit.models import SystemLog
from apps.reflection.models import CodingResult, Cohort


class SystemAPITestCase(APITestCase):
    def setUp(self):
        Cohort.objects.create(name="2023届")
        Cohort.objects.create(name="2022届")

        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
            role=User.ROLE_ADMIN,
            real_name="管理员",
        )
        self.teacher = User.objects.create_user(
            username="111",
            password="password123",
            role=User.ROLE_TEACHER,
            real_name="李四",
            gender="男",
            phone="13500000002",
        )
        self.student = User.objects.create_user(
            username="010",
            password="password123",
            role=User.ROLE_STUDENT,
            real_name="张三",
            cohort="2023届",
            gender="男",
            phone="13500000001",
        )
        self.other_student = User.objects.create_user(
            username="002",
            password="password123",
            role=User.ROLE_STUDENT,
            real_name="张明",
            cohort="2022届",
            gender="男",
            phone="15098751352",
        )
        CodingResult.objects.create(
            student_no="010",
            article_no="文章编号10",
            cohort="2023届",
            segment_no="片段编号1",
            segment_order=1,
            source_row_no=1,
            problem_description=1,
            cause_analysis=1,
            descriptive_reflection=1,
        )
        CodingResult.objects.create(
            student_no="002",
            article_no="文章编号2",
            cohort="2022届",
            segment_no="片段编号1",
            segment_order=1,
            source_row_no=2,
            improvement_strategy=1,
            dialogic_reflection=1,
        )

    def _login(self, username: str, password: str, role: str) -> str:
        resp = self.client.post(
            "/api/auth/login/",
            {"username": username, "password": password, "role": role},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        return resp.data["access"]

    def _auth_header(self, token: str):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_role_checked_login_and_registration(self):
        # Role mismatch must be rejected
        bad_resp = self.client.post(
            "/api/auth/login/",
            {"username": "010", "password": "password123", "role": "teacher"},
            format="json",
        )
        self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Student registration
        reg_student = self.client.post(
            "/api/auth/register/student/",
            {
                "student_no": "2023099",
                "password": "password123",
                "confirm_password": "password123",
                "name": "测试学生",
                "cohort": "2023届",
                "gender": "女",
                "phone": "13811112222",
            },
            format="json",
        )
        self.assertEqual(reg_student.status_code, status.HTTP_201_CREATED)

        # Teacher registration (gender & phone optional per prototype)
        reg_teacher = self.client.post(
            "/api/auth/register/teacher/",
            {
                "teacher_no": "T999",
                "name": "测试教师",
                "password": "password123",
                "confirm_password": "password123",
            },
            format="json",
        )
        self.assertEqual(reg_teacher.status_code, status.HTTP_201_CREATED)

    def test_student_isolation_and_teacher_readonly_rbac(self):
        # Student sees only own coding results & cannot access students/teachers/logs
        student_token = self._login("010", "password123", "student")
        self._auth_header(student_token)

        coding_resp = self.client.get("/api/coding-results/")
        self.assertEqual(coding_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(coding_resp.data["count"], 1)
        self.assertEqual(coding_resp.data["results"][0]["student_no"], "010")

        self.assertEqual(self.client.get("/api/students/").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get("/api/logs/").status_code, status.HTTP_403_FORBIDDEN)

        # Teacher can view all students & coding results, but cannot create/delete
        teacher_token = self._login("111", "password123", "teacher")
        self._auth_header(teacher_token)

        self.assertEqual(self.client.get("/api/students/").status_code, status.HTTP_200_OK)
        all_coding = self.client.get("/api/coding-results/")
        self.assertEqual(all_coding.status_code, status.HTTP_200_OK)
        self.assertEqual(all_coding.data["count"], 2)

        create_denied = self.client.post(
            "/api/students/",
            {"student_no": "999", "student_name": "无权新增"},
            format="json",
        )
        self.assertEqual(create_denied.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_strict_coding_import_validation_and_export(self):
        admin_token = self._login("admin", "admin123", "admin")
        self._auth_header(admin_token)

        # 1) Invalid Excel (non-binary code value 2 + cohort conflict with existing student 010)
        bad_df = pd.DataFrame(
            [
                {
                    "学生学号": "010",
                    "文章编号": "文章编号10",
                    "届别": "2022届",  # conflicts with existing 2023届
                    "片段编号": "片段编号2",
                    "片段顺序": 2,
                    "来源表行号": 10,
                    "问题描述": 2,  # invalid non-binary code
                    "原因分析": 1,
                    "改进策略": 0,
                    "有效性评估": 0,
                    "描述层": 0,
                    "描述性反思": 1,
                    "对话性反思": 0,
                    "批判性反思": 0,
                }
            ]
        )
        bad_buf = io.BytesIO()
        bad_df.to_excel(bad_buf, index=False, engine="openpyxl")
        bad_file = SimpleUploadedFile(
            "bad_coding.xlsx",
            bad_buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        bad_resp = self.client.post("/api/coding-results/import/", {"file": bad_file}, format="multipart")
        self.assertEqual(bad_resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertGreaterEqual(len(bad_resp.data["errors"]), 2)
        self.assertEqual(CodingResult.objects.count(), 2)  # zero partial writes

        # 2) Valid Excel import
        good_df = pd.DataFrame(
            [
                {
                    "学生学号": "010",
                    "文章编号": "文章编号10",
                    "届别": "2023届",
                    "片段编号": "片段编号2",
                    "片段顺序": 2,
                    "来源表行号": 11,
                    "问题描述": 1,
                    "原因分析": 0,
                    "改进策略": 1,
                    "有效性评估": 1,
                    "描述层": 0,
                    "描述性反思": 0,
                    "对话性反思": 1,
                    "批判性反思": 0,
                }
            ]
        )
        good_buf = io.BytesIO()
        good_df.to_excel(good_buf, index=False, engine="openpyxl")
        good_file = SimpleUploadedFile(
            "good_coding.xlsx",
            good_buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        good_resp = self.client.post("/api/coding-results/import/", {"file": good_file}, format="multipart")
        self.assertEqual(good_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(good_resp.data["imported"], 1)
        self.assertEqual(CodingResult.objects.count(), 3)

        # 3) Export Excel & verify system log recorded
        export_resp = self.client.get("/api/coding-results/export/")
        self.assertEqual(export_resp.status_code, status.HTTP_200_OK)
        self.assertIn("spreadsheetml", export_resp["Content-Type"])
        self.assertTrue(SystemLog.objects.filter(module="编码结果", action="批量导入").exists())

    def test_profile_and_password_change(self):
        token = self._login("010", "password123", "student")
        self._auth_header(token)

        put_resp = self.client.put(
            "/api/auth/profile/",
            {"real_name": "张三丰", "phone": "13999998888"},
            format="json",
        )
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(put_resp.data["real_name"], "张三丰")

        pwd_resp = self.client.post(
            "/api/auth/change-password/",
            {
                "old_password": "password123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
            format="json",
        )
        self.assertEqual(pwd_resp.status_code, status.HTTP_200_OK)
        self._login("010", "newpassword123", "student")
