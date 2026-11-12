# 本体领航员 · Ontology Navigator

基于 **Palantir Foundry Ontology 成功实践**的 WorkBuddy 专家（Agent 型）。帮助企业设计业务本体、构建语义层并推动落地采纳，让数据模型真正驱动业务决策与 AI 应用。

## 类型

Agent 型（单个 AI 专家）· 分类：数据智能（04-DataAI）· 版本：1.3.0

## 功能

- **业务诊断与场景锚定**：从模糊诉求中锁定"高价值、可验证、有 owner"的试点场景（价值 × 可行性 × 意愿三维评估）
- **本体三层建模**：Palantir 式对象类型（Object Types）/ 链接类型（Link Types）/ 动作类型（Action Types），输出结构化建模表
- **语义层技术方案**：适配数仓、图数据库、LLM + 知识图谱等任意技术栈；Foundry 环境下给出具体配置建议
- **AI 与本体结合规划**：让 AI Agent 读对象、执行受控动作、全程可审计
- **推行策略与治理**：30/60/90 天推行路线图、采纳率度量看板、概念变更治理机制
- **内置交付物模板**（ontology-toolkit skill）：三层建模表模板、90 天路线图模板、本体诊断问卷

## 工作原则

首轮响应遵循"先交货，后提问"铁律：无论用户提供多少信息，首轮必含实质交付物；信息不足时基于显式行业假设直接产出完整初版，每轮最多 3 个具体确认问题。

## 使用示例

- 「我们是一家有 3 座工厂的工业设备制造商，想用一套业务本体打通销售、交付与售后数据。请直接给出：锚定场景建议、三层建模表初版，以及 90 天落地路线图。」
- 「请以售后维修场景为例演示对象类型/链接类型/动作类型框架，输出三张已填好示例行的建模表。」
- 「我们的本体上线 3 个月，业务团队月活不足 10%。请诊断原因并给出 90 天采纳率拯救计划。」

## 头像

头像位于 `avatars/expert.png`（512×512，453KB）。如需替换为自定义头像，要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB

## 安装

**方式一（推荐）**：从 GitHub 仓库下载 `dist/ontology-navigator.zip`，在 WorkBuddy 专家中心 → 我的专家 中导入。

**方式二**：将本目录复制到专家目录：

```
~/.workbuddy/plugins/marketplaces/my-experts/plugins/ontology-navigator/
```

然后运行注册命令使其可见：

```bash
python3 scripts/register_expert.py <expert-dir>
```

## 打包分享

```bash
python3 scripts/package_expert.py <expert-dir> [output-dir]
```
