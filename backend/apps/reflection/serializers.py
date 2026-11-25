from __future__ import annotations

from rest_framework import serializers

from apps.reflection.models import CodingResult, Cohort


class CohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cohort
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value: str) -> str:
        val = value.strip()
        if not val:
            raise serializers.ValidationError("届别名称不能为空")
        qs = Cohort.objects.filter(name=val)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("该届别已存在")
        return val


class CodingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingResult
        fields = [
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        for field in [
            "problem_description",
            "cause_analysis",
            "improvement_strategy",
            "effectiveness_eval",
            "description_level",
            "descriptive_reflection",
            "dialogic_reflection",
            "critical_reflection",
        ]:
            val = attrs.get(field, getattr(self.instance, field, 0) if self.instance else 0)
            if val not in (0, 1):
                raise serializers.ValidationError({field: "编码值必须为 0 或 1"})

        student_no = attrs.get("student_no", getattr(self.instance, "student_no", "")).strip()
        article_no = attrs.get("article_no", getattr(self.instance, "article_no", "")).strip()
        cohort = attrs.get("cohort", getattr(self.instance, "cohort", "")).strip()
        segment_no = attrs.get("segment_no", getattr(self.instance, "segment_no", "")).strip()
        segment_order = attrs.get("segment_order", getattr(self.instance, "segment_order", None))

        qs_base = CodingResult.objects.all()
        if self.instance is not None:
            qs_base = qs_base.exclude(pk=self.instance.pk)

        if qs_base.filter(student_no=student_no, article_no=article_no, segment_no=segment_no).exists():
            raise serializers.ValidationError("该学生同文章下已存在相同片段编号")
        if qs_base.filter(student_no=student_no, article_no=article_no, segment_order=segment_order).exists():
            raise serializers.ValidationError("该学生同文章下已存在相同片段顺序")

        conflict_cohort = qs_base.filter(student_no=student_no).exclude(cohort=cohort).first()
        if conflict_cohort:
            raise serializers.ValidationError(
                f"学号 {student_no} 的届别与已有记录冲突（已有：{conflict_cohort.cohort}）"
            )
        conflict_article = qs_base.filter(student_no=student_no).exclude(article_no=article_no).first()
        if conflict_article:
            raise serializers.ValidationError(
                f"学号 {student_no} 的文章编号与已有记录冲突（已有：{conflict_article.article_no}）"
            )

        return attrs
