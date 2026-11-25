# Ontology RAG 技能（本体知识检索）

为「本体领航员」提供**深度方法论知识的按需检索**能力。基于本地零依赖向量库（TF-IDF + 余弦相似度），无需联网、无需 pip 安装。

## 何时使用（触发条件）

仅在遇到以下深度问题时调用，常规建模/路线图任务直接用专家正文规则作答，**不必检索**：

1. 常见**反模式**与规避方法
2. **Action Type** 设计细则（五问）
3. **身份解析**（Entity Resolution）四级策略
4. **AIP / 大模型 grounding** 架构
5. **采纳度量**指标体系
6. 需引用本专家方法论原文或评测场景细节

## 如何调用

### 标准接口（专家会话内）

```python
result = skill_main("query_knowledge", {"query": "身份解析怎么做", "top_k": 3})
# result = {"success": True, "context": "【来源：...】\n命中片段..."}
```

- `query`：用户问题或其核心关键词（建议提炼成 2-6 个关键词，命中率更高）
- `top_k`：返回片段数，默认 3，最大建议 5
- 返回 `context` 字段为可直接使用的中文上下文块，含每条命中的来源文件

要拿结构化结果（分数/来源/原文），用 action `query_knowledge_json`。

### 命令行（调试 / 手动验证）

```bash
python ontology_rag.py query "反模式" 3        # 检索并打印命中片段与分数
python ontology_rag.py stats                   # 查看索引块数与来源
python ontology_rag_inject.py "身份解析" 3      # 输出可注入 system prompt 的上下文块
```

## 如何使用检索结果

- 把 `context` 中的命中片段作为**事实依据**融入回答，关键结论后可标注来源文件（如"据 palantir-ontology-methodology.md"）。
- 若返回"（未命中相关材料…）"或片段与问题明显无关，**退回通用方法论作答并如实说明**，禁止编造引用或来源。
- 检索是辅助，不替代首次交付：即使检索无结果，也必须先给出实质回答，再补充说明素材缺失。

## 文件清单

| 文件 | 用途 |
|------|------|
| `ontology_rag.py` | 核心向量库：分词 / TF-IDF / 余弦检索 / 建库 CLI |
| `ontology_rag_skill.py` | 标准 skill 接口 `skill_main(action, params)` |
| `ontology_rag_inject.py` | 上下文构建器 CLI（供应用层注入 system prompt） |
| `ontology_rag_integration.py` | embedding 升级插槽：重写 `EmbeddingVectorStore.embed()` 可接真向量模型 |
| `ontology_vectorstore.json` | 持久化索引（42 块：专家 MD / references / skills / 评测集） |

## 维护提示

- 知识源（agent MD、references、评测集）变更后需重建索引，重建时排除 `ontology_vectorstore.json` 自身，避免自索引污染。
- 当前为纯 Python TF-IDF 方案，对"用词不同但语义相近"的查询泛化有限；升级真 embedding 只需替换 `embed()`，其余检索逻辑不变。
