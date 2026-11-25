from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_STUDENT = "student"
    ROLE_TEACHER = "teacher"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = (
        (ROLE_STUDENT, "学生"),
        (ROLE_TEACHER, "教师"),
        (ROLE_ADMIN, "管理员"),
    )

    GENDER_CHOICES = (
        ("男", "男"),
        ("女", "女"),
    )

    role = models.CharField("角色", max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT, db_index=True)
    real_name = models.CharField("姓名", max_length=64, blank=True, default="")
    cohort = models.CharField("届别", max_length=32, blank=True, default="", db_index=True)
    gender = models.CharField("性别", max_length=10, blank=True, default="")
    phone = models.CharField("手机号", max_length=20, blank=True, default="")
    avatar = models.CharField("头像地址", max_length=255, blank=True, default="")

    class Meta:
        db_table = "sys_user"
        ordering = ["-id"]
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
