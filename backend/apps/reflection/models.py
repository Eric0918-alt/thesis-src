from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

BINARY_VALIDATORS = [MinValueValidator(0), MaxValueValidator(1)]


class Cohort(models.Model):
    name = models.CharField("届别", max_length=32, unique=True, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "reflection_cohort"
        ordering = ["id"]
        verbose_name = "届别"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.name


class CodingResult(models.Model):
    student_no = models.CharField("学生学号", max_length=64, db_index=True)
    article_no = models.CharField("文章编号", max_length=64, db_index=True)
    cohort = models.CharField("届别", max_length=32, db_index=True)
    segment_no = models.CharField("片段编号", max_length=64)
    segment_order = models.PositiveIntegerField("片段顺序")
    source_row_no = models.PositiveIntegerField("来源表行号")

    # 8个反思要素编码（严格二值 0 / 1，不在系统内自动推断或补写）
    problem_description = models.SmallIntegerField("问题描述", default=0, validators=BINARY_VALIDATORS)
    cause_analysis = models.SmallIntegerField("原因分析", default=0, validators=BINARY_VALIDATORS)
    improvement_strategy = models.SmallIntegerField("改进策略", default=0, validators=BINARY_VALIDATORS)
    effectiveness_eval = models.SmallIntegerField("有效性评估", default=0, validators=BINARY_VALIDATORS)
    description_level = models.SmallIntegerField("描述层", default=0, validators=BINARY_VALIDATORS)
    descriptive_reflection = models.SmallIntegerField("描述性反思", default=0, validators=BINARY_VALIDATORS)
    dialogic_reflection = models.SmallIntegerField("对话性反思", default=0, validators=BINARY_VALIDATORS)
    critical_reflection = models.SmallIntegerField("批判性反思", default=0, validators=BINARY_VALIDATORS)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "reflection_coding_result"
        ordering = ["-id"]
        verbose_name = "编码结果"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=["student_no", "article_no", "segment_no"],
                name="uniq_student_article_segment_no",
            ),
            models.UniqueConstraint(
                fields=["student_no", "article_no", "segment_order"],
                name="uniq_student_article_segment_order",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student_no}-{self.article_no}-{self.segment_no}"
