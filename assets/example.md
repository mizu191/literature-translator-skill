# 最小调用示例（示意，非正式案例结果）

> 以下输入、调用与输出仅用于说明本 Skill 的接口与完整使用流程，**不代表任何正式测试案例的结果**。

## 示意输入

`/input/case.json`（节选）：

```json
{
  "case_id": "demo-000",
  "task": "把 paper.pdf 第 1–2 节的正文与图注翻译成中文双语对照",
  "material": "/input/paper.pdf",
  "direction": "en→zh",
  "output_contract": {
    "translation": "bilingual.md",
    "glossary": "glossary.md",
    "verification": "verification.md"
  }
}
```

## 调用方式（Agent 按 SKILL.md 执行）

1. 读 `/input/case.json` 与 `/input/task.md`，确定范围：第 1–2 节正文与图注，英→中。
2. 提取 PDF 文字层，建立 `source-paragraphs.md`，分配 `P1…Pn`、`FIG1…`。
3. 抽取术语写入 `glossary.md`（如 `Bayesian inference → 贝叶斯推断`）。
4. 逐段翻译，输出 `bilingual.md`。
5. 自检数字/单位/公式/编号/引用/否定，输出 `verification.md`。
6. 写 `result.json`，覆盖 `output_contract` 字段并追加 `status/sources/uncertainty/change_records`。

## 示意输出（节选）

`bilingual.md`：

```markdown
### P1 · §1 Introduction · p1

**原文**
> Bayesian inference provides a principled framework ...

**译文**
> 贝叶斯推断提供了一种有原则的框架……

**定位**：p1，§1，P1　**译法依据**：术语按 glossary.md 锁定译名；未改动数字与公式。
```

`result.json`（节选）：

```json
{
  "case_id": "demo-000",
  "status": "success",
  "translation": "bilingual.md",
  "glossary": "glossary.md",
  "verification": "verification.md",
  "sources": [{"claim": "首段引入贝叶斯推断框架", "loc": {"page": 1, "unit_id": "P1"}}],
  "uncertainty": [],
  "change_records": [{"time": "2026-11-26T00:00:00Z", "change": "锁定 Bayesian inference → 贝叶斯推断"}]
}
```

## 说明

- 实际运行时以 `/input/case.json` 的 `output_contract` 为准，字段名可能与示例不同。
- 示例中的文献与数据为构造内容，仅演示格式。
