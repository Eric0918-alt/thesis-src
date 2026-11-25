from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd

from apps.reflection.models import CodingResult

COLUMN_TO_FIELD: List[Tuple[str, str]] = [
    ("学生学号", "student_no"),
    ("文章编号", "article_no"),
    ("届别", "cohort"),
    ("片段编号", "segment_no"),
    ("片段顺序", "segment_order"),
    ("来源表行号", "source_row_no"),
    ("问题描述", "problem_description"),
    ("原因分析", "cause_analysis"),
    ("改进策略", "improvement_strategy"),
    ("有效性评估", "effectiveness_eval"),
    ("描述层", "description_level"),
    ("描述性反思", "descriptive_reflection"),
    ("对话性反思", "dialogic_reflection"),
    ("批判性反思", "critical_reflection"),
]

CODE_COLUMNS: List[Tuple[str, str]] = COLUMN_TO_FIELD[6:]
REQUIRED_COLUMNS: List[str] = [col for col, _ in COLUMN_TO_FIELD]


def _parse_positive_int(raw: str) -> Tuple[bool, int]:
    text = raw.strip()
    if not text:
        return False, 0
    try:
        if "." in text:
            val_f = float(text)
            if not val_f.is_integer():
                return False, 0
            val = int(val_f)
        else:
            val = int(text)
    except ValueError:
        return False, 0
    return (val >= 1), val


def _parse_binary_code(raw: str) -> Tuple[bool, int]:
    text = raw.strip()
    if not text:
        return False, 0
    try:
        if "." in text:
            val_f = float(text)
            if not val_f.is_integer():
                return False, 0
            val = int(val_f)
        else:
            val = int(text)
    except ValueError:
        return False, 0
    return (val in (0, 1)), val


def validate_coding_dataframe(df: pd.DataFrame) -> Tuple[List[CodingResult], List[Dict[str, object]]]:
    """
    严格按开题报告约定校验已有编码结果文件：
    1. 核对必填列齐全，不自动补写或推断缺失编码；
    2. 校验必填标识字段非空、片段顺序与来源表行号为正整数；
    3. 校验8个反思编码字段严格取值为 0 或 1；
    4. 校验文件内及库内 (学生学号, 文章编号, 片段编号) 与 (学生学号, 文章编号, 片段顺序) 不重复；
    5. 校验同一学生学号对应的届别和文章编号不存在冲突。
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        return [], [
            {
                "row": 1,
                "field": "表头",
                "reason": f"缺少必填列：{', '.join(missing_cols)}",
            }
        ]

    if df.empty:
        return [], [{"row": 2, "field": "文件", "reason": "导入文件不包含任何数据行"}]

    errors: List[Dict[str, object]] = []
    valid_objects: List[CodingResult] = []

    existing_seg_no = set(
        CodingResult.objects.values_list("student_no", "article_no", "segment_no")
    )
    existing_seg_order = set(
        CodingResult.objects.values_list("student_no", "article_no", "segment_order")
    )
    existing_student_cohort: Dict[str, str] = {}
    existing_student_article: Dict[str, str] = {}
    for s_no, a_no, cohort_val in CodingResult.objects.values_list("student_no", "article_no", "cohort").distinct():
        existing_student_cohort.setdefault(s_no, cohort_val)
        existing_student_article.setdefault(s_no, a_no)

    seen_seg_no = set()
    seen_seg_order = set()
    file_student_cohort: Dict[str, str] = {}
    file_student_article: Dict[str, str] = {}

    for idx, row in df.iterrows():
        row_num = int(idx) + 2
        row_has_error = False

        student_no = str(row["学生学号"]).strip()
        article_no = str(row["文章编号"]).strip()
        cohort = str(row["届别"]).strip()
        segment_no = str(row["片段编号"]).strip()

        for col_name, val in [
            ("学生学号", student_no),
            ("文章编号", article_no),
            ("届别", cohort),
            ("片段编号", segment_no),
        ]:
            if not val:
                errors.append({"row": row_num, "field": col_name, "reason": f"{col_name}不能为空"})
                row_has_error = True

        ok_order, segment_order = _parse_positive_int(str(row["片段顺序"]))
        if not ok_order:
            errors.append({"row": row_num, "field": "片段顺序", "reason": "片段顺序必须为正整数"})
            row_has_error = True

        ok_src_row, source_row_no = _parse_positive_int(str(row["来源表行号"]))
        if not ok_src_row:
            errors.append({"row": row_num, "field": "来源表行号", "reason": "来源表行号必须为正整数"})
            row_has_error = True

        code_values: Dict[str, int] = {}
        for col_name, field_name in CODE_COLUMNS:
            raw_val = str(row[col_name])
            ok_bin, bin_val = _parse_binary_code(raw_val)
            if not ok_bin:
                errors.append(
                    {
                        "row": row_num,
                        "field": col_name,
                        "reason": f"非法取值“{raw_val.strip() or '空'}”，编码值必须为 0 或 1（系统不自动补写）",
                    }
                )
                row_has_error = True
            else:
                code_values[field_name] = bin_val

        if student_no and cohort:
            if student_no in existing_student_cohort and existing_student_cohort[student_no] != cohort:
                errors.append(
                    {
                        "row": row_num,
                        "field": "届别",
                        "reason": f"学号 {student_no} 与已有记录届别冲突（库内：{existing_student_cohort[student_no]}，当前：{cohort}）",
                    }
                )
                row_has_error = True
            elif student_no in file_student_cohort and file_student_cohort[student_no] != cohort:
                errors.append(
                    {
                        "row": row_num,
                        "field": "届别",
                        "reason": f"文件内学号 {student_no} 对应多个届别（{file_student_cohort[student_no]} / {cohort}）",
                    }
                )
                row_has_error = True
            else:
                file_student_cohort[student_no] = cohort

        if student_no and article_no:
            if student_no in existing_student_article and existing_student_article[student_no] != article_no:
                errors.append(
                    {
                        "row": row_num,
                        "field": "文章编号",
                        "reason": f"学号 {student_no} 与已有文章编号冲突（库内：{existing_student_article[student_no]}，当前：{article_no}）",
                    }
                )
                row_has_error = True
            elif student_no in file_student_article and file_student_article[student_no] != article_no:
                errors.append(
                    {
                        "row": row_num,
                        "field": "文章编号",
                        "reason": f"文件内学号 {student_no} 对应多个文章编号（{file_student_article[student_no]} / {article_no}）",
                    }
                )
                row_has_error = True
            else:
                file_student_article[student_no] = article_no

        if student_no and article_no and segment_no:
            seg_key = (student_no, article_no, segment_no)
            if seg_key in seen_seg_no:
                errors.append({"row": row_num, "field": "片段编号", "reason": f"文件内重复记录：{student_no}-{article_no}-{segment_no}"})
                row_has_error = True
            elif seg_key in existing_seg_no:
                errors.append({"row": row_num, "field": "片段编号", "reason": f"系统中已存在记录：{student_no}-{article_no}-{segment_no}"})
                row_has_error = True
            else:
                seen_seg_no.add(seg_key)

        if student_no and article_no and ok_order:
            ord_key = (student_no, article_no, segment_order)
            if ord_key in seen_seg_order:
                errors.append({"row": row_num, "field": "片段顺序", "reason": f"文件内片段顺序重复：{student_no}-{article_no}-顺序{segment_order}"})
                row_has_error = True
            elif ord_key in existing_seg_order:
                errors.append({"row": row_num, "field": "片段顺序", "reason": f"系统中已存在该片段顺序：{student_no}-{article_no}-顺序{segment_order}"})
                row_has_error = True
            else:
                seen_seg_order.add(ord_key)

        if not row_has_error:
            valid_objects.append(
                CodingResult(
                    student_no=student_no,
                    article_no=article_no,
                    cohort=cohort,
                    segment_no=segment_no,
                    segment_order=segment_order,
                    source_row_no=source_row_no,
                    **code_values,
                )
            )

    if errors:
        return [], errors
    return valid_objects, []
