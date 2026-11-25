from __future__ import annotations

from django.db import models


class SystemLog(models.Model):
    STATUS_SUCCESS = "成功"
    STATUS_FAILED = "失败"
    STATUS_CHOICES = (
        (STATUS_SUCCESS, "成功"),
        (STATUS_FAILED, "失败"),
    )

    username = models.CharField("操作用户", max_length=64, db_index=True)
    role = models.CharField("用户角色", max_length=32, blank=True, default="")
    module = models.CharField("操作模块", max_length=64, db_index=True)
    action = models.CharField("操作类型", max_length=64)
    method = models.CharField("请求方法", max_length=16, default="POST")
    path = models.CharField("请求路径", max_length=255, blank=True, default="")
    detail = models.TextField("操作详情", blank=True, default="")
    ip_address = models.CharField("IP地址", max_length=64, blank=True, default="")
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default=STATUS_SUCCESS)
    created_at = models.DateTimeField("操作时间", auto_now_add=True, db_index=True)

    class Meta:
        db_table = "sys_log"
        ordering = ["-created_at", "-id"]
        verbose_name = "系统日志"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"[{self.created_at}] {self.username} - {self.module}:{self.action}"
