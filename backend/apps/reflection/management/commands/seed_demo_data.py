from __future__ import annotations

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from apps.accounts.models import User
from apps.audit.models import SystemLog
from apps.reflection.models import CodingResult, Cohort


def _ensure_avatar(filename: str, bg_color: tuple, accent_color: tuple) -> str:
    avatar_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    filepath = os.path.join(avatar_dir, filename)
    if not os.path.exists(filepath):
        img = Image.new("RGB", (160, 160), bg_color)
        draw = ImageDraw.Draw(img)
        # Draw a clean stylized portrait silhouette
        draw.ellipse((52, 28, 108, 84), fill=accent_color)
        draw.pieslice((24, 88, 136, 192), start=180, end=360, fill=accent_color)
        img.save(filepath, "PNG")
    return f"{settings.MEDIA_URL}avatars/{filename}"


class Command(BaseCommand):
    help = "初始化系统演示数据（管理员、教师、学生、届别、编码结果、系统日志）"

    def handle(self, *args, **options):
        cohorts = ["2017届", "2021届", "2028届", "2016届", "2019届", "2020届", "2022届", "2023届"]
        for name in cohorts:
            Cohort.objects.get_or_create(name=name)

        admin_avatar = _ensure_avatar("seed_admin.png", (219, 234, 254), (37, 99, 235))
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123",
                role=User.ROLE_ADMIN,
                real_name="系统管理员",
                gender="男",
                phone="13800000000",
                avatar=admin_avatar,
            )

        teachers = [
            ("111", "李四", "男", "13500000002", (219, 234, 254), (29, 78, 216)),
            ("105", "王静", "男", "13556789012", (224, 242, 254), (2, 132, 199)),
            ("106", "张伟", "男", "13467890123", (226, 232, 240), (71, 85, 105)),
            ("102", "刘洋", "男", "13578901234", (220, 252, 231), (22, 163, 74)),
            ("107", "张雨", "女", "13589012345", (252, 231, 243), (219, 39, 119)),
            ("108", "李娜", "女", "13490123456", (237, 233, 254), (124, 58, 237)),
        ]
        for t_no, t_name, gender, phone, bg, fg in teachers:
            avatar_url = _ensure_avatar(f"seed_teacher_{t_no}.png", bg, fg)
            if not User.objects.filter(username=t_no).exists():
                User.objects.create_user(
                    username=t_no,
                    password="123456",
                    role=User.ROLE_TEACHER,
                    real_name=t_name,
                    gender=gender,
                    phone=phone,
                    avatar=avatar_url,
                )

        students = [
            ("010", "张三", "2023届", "男", "13500000001", (219, 234, 254), (30, 64, 175)),
            ("002", "张明", "2017届", "男", "15098751352", (254, 226, 226), (185, 28, 28)),
            ("008", "孙雨晴", "2021届", "男", "13023456789", (252, 231, 243), (190, 24, 93)),
            ("007", "李思远", "2028届", "男", "13189065234", (224, 242, 254), (3, 105, 161)),
            ("004", "刘芳", "2016届", "女", "13277541235", (226, 232, 240), (51, 65, 85)),
            ("003", "吴磊", "2019届", "女", "13678962345", (220, 252, 231), (21, 128, 61)),
            ("001", "陈晨", "2020届", "女", "13712345678", (254, 243, 199), (180, 83, 9)),
            ("006", "林雪", "2022届", "女", "13823456789", (237, 233, 254), (109, 40, 217)),
            ("005", "周杰", "2023届", "男", "13934567890", (207, 250, 254), (14, 116, 144)),
        ]
        for s_no, s_name, cohort, gender, phone, bg, fg in students:
            avatar_url = _ensure_avatar(f"seed_student_{s_no}.png", bg, fg)
            if not User.objects.filter(username=s_no).exists():
                User.objects.create_user(
                    username=s_no,
                    password="123456",
                    role=User.ROLE_STUDENT,
                    real_name=s_name,
                    cohort=cohort,
                    gender=gender,
                    phone=phone,
                    avatar=avatar_url,
                )

        # 初始化与原型图对应的编码结果演示记录
        coding_rows = [
            ("005", "文章编号1", "2023届", "片段编号1", 1, 1, 1, 1, 0, 0, 0, 1, 0, 0),
            ("006", "文章编号2", "2022届", "片段编号2", 2, 2, 1, 0, 1, 0, 0, 1, 0, 0),
            ("001", "文章编号3", "2020届", "片段编号3", 3, 3, 1, 1, 1, 0, 0, 0, 1, 0),
            ("003", "文章编号4", "2019届", "片段编号4", 4, 4, 0, 1, 1, 1, 0, 0, 1, 0),
            ("004", "文章编号5", "2016届", "片段编号5", 5, 5, 1, 0, 0, 0, 1, 0, 0, 0),
            ("007", "文章编号6", "2028届", "片段编号6", 6, 6, 1, 1, 1, 1, 0, 0, 1, 1),
            ("008", "文章编号7", "2021届", "片段编号7", 7, 7, 1, 1, 0, 0, 0, 1, 0, 0),
            ("002", "文章编号8", "2017届", "片段编号8", 8, 8, 0, 0, 1, 1, 0, 0, 0, 1),
        ]
        for (
            s_no,
            a_no,
            cohort,
            seg_no,
            seg_order,
            src_row,
            p_desc,
            c_ana,
            i_str,
            e_eval,
            d_lvl,
            d_ref,
            dia_ref,
            cri_ref,
        ) in coding_rows:
            CodingResult.objects.get_or_create(
                student_no=s_no,
                article_no=a_no,
                segment_no=seg_no,
                defaults={
                    "cohort": cohort,
                    "segment_order": seg_order,
                    "source_row_no": src_row,
                    "problem_description": p_desc,
                    "cause_analysis": c_ana,
                    "improvement_strategy": i_str,
                    "effectiveness_eval": e_eval,
                    "description_level": d_lvl,
                    "descriptive_reflection": d_ref,
                    "dialogic_reflection": dia_ref,
                    "critical_reflection": cri_ref,
                },
            )

        if not SystemLog.objects.exists():
            SystemLog.objects.bulk_create(
                [
                    SystemLog(
                        username="admin",
                        role="管理员",
                        module="系统初始化",
                        action="初始化基础数据",
                        method="SYSTEM",
                        path="/manage/seed_demo_data",
                        detail="初始化 8 个届别、6 名教师、9 名学生与 8 条编码结果演示数据",
                        ip_address="127.0.0.1",
                        status=SystemLog.STATUS_SUCCESS,
                    ),
                    SystemLog(
                        username="111",
                        role="教师",
                        module="认证登录",
                        action="用户登录",
                        method="POST",
                        path="/api/auth/login/",
                        detail="用户 111（教师）登录系统",
                        ip_address="127.0.0.1",
                        status=SystemLog.STATUS_SUCCESS,
                    ),
                ]
            )

        self.stdout.write(self.style.SUCCESS("演示数据初始化完成！"))
