# 输出契约与 result.json 规则（output-contract）

## 关键原则

- 最终结构化结果写 `/app/output/result.json`。
- **以实际 `/input/case.json` 的 `output_contract` 为准**：逐字段覆盖，不臆造字段名、不遗漏字段。
- 除 `output_contract` 声明的字段外，统一追加四个字段：`case_id`、`status`、`sources`、`uncertainty`、`change_records`（若契约已用同名键，则合并内容，不覆盖语义）。

## 字段约定

### case_id

字符串，来自 `/input/case.json`。缺失时写 `"unknown"` 并在 `uncertainty` 说明。

### 主结果字段

按 `output_contract` 原样输出。若契约要求"答案/翻译/结构化字段/知识结构"，把双语对照、术语表、核验清单的核心内容放入对应字段，并附带产物文件名。

### status

枚举：`success` / `partial` / `unable` / `refused`。每条写清原因与可人工接管位置：

- `success`：覆盖任务要求范围，且关键结论能回到材料定位；
- `partial`：部分完成，明确列出已完成与未完成边界；
- `unable`：材料缺失/解析失败等导致无法完成，说明具体原因；
- `refused`：任务超出可安全执行范围（极少用），说明拒绝理由。

### sources

关键结论的原文定位：页码、段号（`unit_id`）、图/表/公式编号、章节。格式：

```text
[{"claim":"...","loc":{"page":3,"unit_id":"P7","snippet":"..."}}, ...]
```

### uncertainty

未报告、无法判断、材料冲突、OCR 低置信、需人工确认项。逐条给定位与原因，不写成事实。

### change_records

本次运行的关键改动：术语锁定调整、跨页段落合并、译文回改、OCR 兜底等。每条带时间与说明。

## 产物清单（写 `/app/output`）

- `bilingual.md`：双语对照主结果（段落级对齐，带 `unit_id` 与页码定位）。
- `glossary.md`：术语表（含变体与锁定译名）。
- `verification.md`：自检结果与"需人工确认清单"。
- 其它可编辑产物（如 Office/图示）需渲染 PDF/PNG 预览，便于人工检查。

## result.json 最小骨架

见 `../assets/result-template.json`。使用时替换占位内容，保留结构。
