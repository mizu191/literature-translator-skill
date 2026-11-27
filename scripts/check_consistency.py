#!/usr/bin/env python3
"""术语一致性与段落完整性自检（literature-translator 配套脚本）。

用途：对双语对照结果做确定性检查，供 Agent 在"第 5 步译文自检"时调用，
也可人工复用。仅依赖标准库。

检查项：
  1. 术语泄漏：术语表中的源词/变体若原样出现在译文段（且不在"保留原文"
     白名单中），报告为疑似未译/译名不一致。
  2. 段落完整性：从 bilingual.md 的单元标题提取 unit_id，
     校验正文 P 段号连续、无重号；图/表/公式/脚注无重号。

用法：
  python3 check_consistency.py --glossary glossary.md --bilingual bilingual.md \
      [--keep-raw terms.txt] [--json out.json]

退出码：0 = 通过；1 = 发现问题；2 = 输入缺失或格式错误。
"""

import argparse
import json
import re
import sys

UNIT_RE = re.compile(r"^#{2,6}\s+(?P<unit>[A-Z]+\d+)\b")
SEP_RE = re.compile(r"^[\s|:|-]+$")


def _cells(line):
    return [c.strip() for c in line.strip("|").split("|")]


def _is_separator(line):
    """Markdown 表格分隔行：|----|----| 或 |-|-|-| 等，去掉管道后仅剩 - : 空格。"""
    if not line.startswith("|"):
        return False
    return bool(SEP_RE.match(line))


def parse_glossary(path):
    """从 Markdown 表格解析术语表，返回 (terms, keep_raw)。

    terms: dict term_lower -> list[source words]，含 term 与 variants 列。
    keep_raw: 术语表中声明"保留原文"的专有项（不被判为泄漏）。
    """
    terms = {}
    keep_raw = set()
    with open(path, "r", encoding="utf-8-sig") as f:
        in_table = False
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if _is_separator(line):
                in_table = True
                continue
            if not in_table:
                continue
            if not line.startswith("|"):
                continue
            cells = _cells(line)
            if not cells or not cells[0]:
                continue
            # 术语表主体：term | translation | variants | ...
            if len(cells) >= 3 and cells[0] not in ("term", "术语"):
                term = cells[0]
                variants = [v.strip() for v in cells[2].split(",") if v.strip()]
                words = [term] + variants
                for w in words:
                    if w:
                        terms[w.lower()] = words
            # "保留原文"表：term | 处理方式
            elif len(cells) >= 2 and cells[0] and ("保留原文" in cells[1] or "不译" in cells[1]):
                keep_raw.add(cells[0].lower())
    return terms, keep_raw


def split_translation_sections(path):
    """把 bilingual.md 切成 (unit_id, 译文正文) 列表，只取'译文'块。"""
    units = []
    current = None
    buf = []
    in_translation = False
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            m = UNIT_RE.match(line)
            if m:
                if current is not None:
                    units.append((current, "\n".join(buf)))
                current = m.group("unit")
                buf = []
                in_translation = False
                continue
            if "**译文**" in line or "**译文（图注）**" in line or "**译文（表题）**" in line:
                in_translation = True
                continue
            if in_translation:
                # 译文块结束标志：定位/译法依据行
                if line.strip().startswith("**定位**") or line.strip().startswith("**译法依据**"):
                    in_translation = False
                    continue
                buf.append(line)
    if current is not None:
        units.append((current, "\n".join(buf)))
    return units


def check_terminology(units, terms, keep_raw):
    issues = []
    for unit, text in units:
        lower = text.lower()
        for term_lower, words in terms.items():
            if term_lower in keep_raw:
                continue
            # 源词原样出现在译文里（未译），视为泄漏
            if term_lower in lower:
                issues.append({
                    "type": "terminology_leak",
                    "unit": unit,
                    "term": words[0],
                    "detail": f"源词/变体'{words[0]}'原样出现在译文",
                })
    return issues


def check_paragraph_completeness(units):
    issues = []
    seen = {}
    for unit, _ in units:
        m = re.match(r"^([A-Z]+)(\d+)$", unit)
        if not m:
            continue
        kind, num = m.group(1), int(m.group(2))
        seen.setdefault(kind, []).append(num)
    for kind, nums in seen.items():
        dupes = sorted({n for n in nums if nums.count(n) > 1})
        for d in dupes:
            issues.append({
                "type": "duplicate_unit",
                "unit": f"{kind}{d}",
                "detail": "重复出现",
            })
        if kind == "P":
            nums_sorted = sorted(nums)
            for a, b in zip(nums_sorted, nums_sorted[1:]):
                if b != a + 1:
                    issues.append({
                        "type": "missing_unit",
                        "unit": f"P{a + 1}",
                        "detail": f"P{a} 之后缺 P{a + 1}",
                    })
                    break  # 只报第一个缺口
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glossary", required=True)
    ap.add_argument("--bilingual", required=True)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    try:
        terms, keep_raw = parse_glossary(args.glossary)
        units = split_translation_sections(args.bilingual)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    issues = check_terminology(units, terms, keep_raw) + \
        check_paragraph_completeness(units)

    report = {
        "glossary_terms": len(terms),
        "bilingual_units": len(units),
        "issues": issues,
        "passed": len(issues) == 0,
    }
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    for it in issues:
        print(f"[{it['type']}] {it['unit']}: {it['detail']}")
    print(f"checked {report['glossary_terms']} terms, "
          f"{report['bilingual_units']} units, "
          f"{len(issues)} issue(s)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
