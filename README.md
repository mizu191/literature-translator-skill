# literature-translator（文献翻译 Skill）

把科研论文（或指定段落区间）翻译成**可核验的双语对照结果**，而不是只给大意或改写。重点解决四个问题：

- **术语稳** — 从原文抽取领域术语并锁定唯一译名，术语表是真实文件、被逐段执行与全篇回填校验；
- **段落全** — 语义边界切分 + 跨页/跨栏合并，稳定段号与原文一一对应，不漏、不重、不错位；
- **关系准** — 数字、单位、公式与编号、图/表编号、文献引用、否定与限定、因果与让步、指代与原文一致；
- **可核验** — 每段译文指回原文定位并说明译法依据，译不准处显式标注 `[待人工确认]`。

这是 Bohrium「阅读03｜文献翻译」挑战（product-arena-01-5a9928c1）的提交作品，可被 Agent（如 DeepSeek Harness）作为 Skill 加载运行。

## 目录

```text
SKILL.md            # 主流程与触发条件（含 name/description frontmatter）
USAGE.md            # 使用与方法说明
references/         # 术语、分段、自检、异常处理、输出契约的详细规则
assets/             # 术语表/双语对照/result.json 模板 + 最小调用示例
scripts/            # 确定性自检脚本（仅标准库）
```

## 快速使用

1. 读入 `/input/case.json` 与 `/input/task.md`，确定材料、翻译范围、方向与 `output_contract`。
2. 按 `SKILL.md` 六步执行：读输入 → 建页面段落结构 → 切分定段号 → 抽术语锁译名 → 逐段双语翻译 → 自检汇总。
3. 产出 `/app/output/bilingual.md`、`glossary.md`、`verification.md`、`result.json`。

## 自检脚本

```bash
python3 scripts/check_consistency.py --glossary glossary.md --bilingual bilingual.md --json check.json
```

机械检查术语源词/变体是否泄漏进译文、段落单元号是否连续无重号。仅依赖 Python 标准库。

详见 `USAGE.md`。
