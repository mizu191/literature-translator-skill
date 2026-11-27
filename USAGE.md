# 文献翻译 Skill（literature-translator）使用与方法说明

## 1. 用途与适用条件

把科研论文（或指定段落区间）翻译成**可复核的双语对照结果**，重点解决四个问题：

- **术语稳**：同一术语全篇锁定同一译名，术语表是真实文件、被真正执行。
- **段落全**：长文跨页/跨栏/跨章不漏段、不重复、不错位，段号与原文一一对应。
- **关系准**：数字、单位、公式、编号、文献引用、否定/限定、因果/让步、指代与原文一致。
- **可核验**：每段译文指回原文定位并说明译法依据，译不准处显式标注。

**适用**：文献翻译、论文翻译、双语对照、术语表抽取、译文核验。
**不适用**：只给大意/改写、只解释概念、只查数据、只写摘要。

## 2. 调用方式

本 Skill 由 Agent 通过 skill 加载后按 `SKILL.md` 执行。对人工用户，等价流程为：

1. 提供输入：`/input/case.json`（含 `case_id`、材料路径、翻译范围、方向、`output_contract`）与 `/input/task.md`。
2. 按 `SKILL.md` 六步执行：读输入 → 读原文建结构 → 切分定段号 → 抽取锁定术语 → 逐段双语翻译 → 自检与汇总。
3. 产物：`bilingual.md`（双语对照）、`glossary.md`（术语表）、`verification.md`（核验清单）、`result.json`（结构化结果）。

## 3. 输入输出

| 项 | 说明 |
|-|-|
| 输入 | `case.json`、`task.md`、原文 PDF/文本；翻译范围与方向可在 `case.json` 中声明 |
| 中间产物 | `/app/work/source-paragraphs.md`（页面—段落结构）、`glossary.md` |
| 最终产物 | `/app/output/bilingual.md`、`glossary.md`、`verification.md`、`result.json` |

`result.json` 必含 `case_id`，并覆盖 `case.json` 的 `output_contract` 全部字段，另追加 `status`、`sources`、`uncertainty`、`change_records`。

## 4. 关键方法

- **术语表驱动**：先抽术语、锁定唯一译名、落地文件，翻译阶段逐段对照，译后全篇回填校验（见 `references/terminology.md`）。
- **稳定段号**：语义边界切分，跨页/跨栏合并，`P<序>`/`FIG`/`TAB`/`EQ`/`FN` 稳定标识（见 `references/segmentation.md`）。
- **保护项翻译**：数字、单位、公式与编号、图/表编号、文献标记、否定/限定原样保留，不因"通顺"而改动。
- **自检清单**：术语一致性、段落完整性、数字单位、公式编号、引用、关系逐项检查，产出"需人工确认清单"（见 `references/verification.md`）。
- **确定性脚本**：`scripts/check_consistency.py` 做术语泄漏与段号连续性的机械检查。

## 5. 适用场景与限制

- 默认方向为英文→中文；其它方向以 `case.json` 为准。
- 公式/表格为图片、扫描件、OCR 低置信处只做可见内容的忠实抄录，并标注 `[待人工确认]`，不猜测。
- 本 Skill 保证"忠实、可核验、术语一致"，不承诺文学性流畅；宁可标注存疑，也不含混处理。
- 参考文献表只译可读部分，作者名/年份/DOI 等保留原文。

## 6. 失败处理与自查

- 异常处置见 `references/failure-handling.md`：文字层缺失→OCR、图片公式→抄录+标注、原文残缺→`[原文缺失]`、材料冲突→以 `case.json` 为准并记录。
- 自查：先跑 `scripts/check_consistency.py`（机械检查），再按 `references/verification.md` 做语义核验，最后核对 `result.json` 是否覆盖 `output_contract` 全部字段。

## 7. 最小调用示例

见 `assets/example.md`（示意，非正式案例结果）。

## 8. 目录结构

提交目录根路径直接放置 `SKILL.md`，资源作为同级子目录：

```text
（提交目录根）/
├── SKILL.md                          # 主流程（评测安装到 /skills/weekly-skill）
├── USAGE.md                          # 使用与方法说明（本文件）
├── references/
│   ├── terminology.md                # 术语抽取与锁定
│   ├── segmentation.md               # 分段与段号
│   ├── verification.md               # 译文自检
│   ├── failure-handling.md           # 异常处理
│   └── output-contract.md            # result.json 约定
├── assets/
│   ├── glossary-template.md          # 术语表模板
│   ├── bilingual-template.md         # 双语对照模板
│   ├── result-template.json          # result.json 骨架
│   └── example.md                    # 最小调用示例
└── scripts/
    └── check_consistency.py          # 确定性自检脚本（仅标准库）
```
