# 本体领航员 · Ontology Navigator

一个基于 **Palantir Foundry Ontology 成功实践**的 WorkBuddy 专家（Agent），帮助企业设计、建模并推行业务本体（Ontology），让数据模型真正驱动业务决策与 AI 应用。

![avatar](avatars/expert.png)

## 核心方法论

源自 Palantir 的五条信条：

1. **决策为中心** — 本体建模的起点是"要改进什么决策"，而非"有哪些数据表"
2. **快赢优先** — 先在一个高价值场景落地见效，再横向复制，拒绝大爆炸式建模
3. **本体是产品不是项目** — 有版本、路线图、反馈闭环和运营机制
4. **语义与物理解耦** — 业务概念稳定，数据管道可演化
5. **AI 时代的地基** — 本体是 AI Agent 的着陆场：对象类型提供上下文，动作类型提供受控操作

## 能做什么

- 业务诊断与试点场景锚定（价值 × 可行性 × 意愿三维评估）
- 三层建模：**对象类型 / 链接类型 / 动作类型**，输出结构化建模表
- 语义层技术方案设计：适配数仓、图数据库、LLM + 知识图谱等任意技术栈
- AI 与本体结合规划：让 Agent 读对象、执行受控 Action、可审计
- 推行策略与治理：试点 → 复制 → 平台化，度量采纳率

## 六步工作流

诊断 → 锚定 → 建模 → 实现 → 推行 → 复盘迭代

## 安装使用

### 方式一：导入安装包（推荐）

从 `dist/ontology-navigator.zip` 下载安装包，在 WorkBuddy **专家中心 → 我的专家** 中导入即可。

### 方式二：手动放置

将本仓库内容复制到：

```
~/.workbuddy/plugins/marketplaces/my-experts/plugins/ontology-navigator/
```

然后重启 WorkBuddy（或重新进入专家中心）即可在专家列表中看到「本体领航员」。

## 目录结构

```
ontology-navigator/
├── .codebuddy-plugin/
│   └── plugin.json          # 专家元数据与展示字段
├── agents/
│   └── ontology-navigator.md # 提示词内核（角色/信念/能力/流程/规范）
├── avatars/
│   └── expert.png           # 专家头像（512×512）
├── dist/
│   └── ontology-navigator.zip # 可直接导入的安装包
└── README.md
```

## License

MIT
