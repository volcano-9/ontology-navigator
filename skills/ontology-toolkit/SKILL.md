---
name: ontology-toolkit
description: "Ontology deliverable templates for the Ontology Navigator expert: three-layer modeling tables (Object/Link/Action), 90-day adoption roadmap, and a business ontology diagnostic questionnaire. Load the matching template from templates/ when producing the corresponding deliverable."
---

# Ontology Toolkit — 本体交付物模板库

为「本体领航员」专家提供标准交付物模板。产出对应交付物时，必须从 `templates/` 加载对应模板并按其结构填写，确保输出一致且可直接落地使用。

## 模板清单

| 模板文件 | 用途 | 触发时机 |
|---------|------|---------|
| `templates/modeling-tables.md` | 三层建模表（对象/链接/动作） | 用户要求建模、梳理对象关系、设计本体结构时 |
| `templates/roadmap-90day.md` | 90 天推行路线图 | 用户要求落地计划、推行方案、采纳率提升计划时 |
| `templates/diagnostic-questionnaire.md` | 本体诊断问卷（10 问） | 用户信息不足需要诊断，或要求评估本体现状时 |

## 使用规则

1. **先加载模板再产出**：禁止脱离模板结构自行发挥，表格列名必须与模板一致。
2. **假设显式化**：模板中无法从用户输入得知的字段，填入带「假设」标注的默认值，并在交付物末尾集中列出"本轮假设"。
3. **示例行保留一格**：每张空表保留一行示例行（斜体或标注"示例"），帮助用户理解填写方式。
4. **中文为主、英文标识配套**：所有对象/链接/动作给出中文名 + 英文标识（PascalCase / camelCase）。
