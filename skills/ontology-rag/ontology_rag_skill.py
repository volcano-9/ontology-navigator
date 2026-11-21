#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ontology_rag_skill.py - 本体领航员专用 skill（把向量库封装为可调用工具）

部署方式：
1. 把此文件 + ontology_rag.py + ontology_vectorstore.json 放到专家包的：
   skills/ontology-rag/ontology_rag_skill.py
   skills/ontology-rag/ontology_rag.py
   skills/ontology-rag/ontology_vectorstore.json
2. 在 plugin.json 的 skills 字段加入 "./skills/ontology-rag"
3. 专家会话中可直接调用 query_knowledge("查询文本", top_k=3)

注意：此 skill 依赖 ontology_rag.py 的 VectorStore 类。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 复用同目录下的 ontology_rag.py
try:
    import ontology_rag
except ImportError:
    print("警告：请将 ontology_rag.py 放在同目录")
    ontology_rag = None


class OntologyRAGSkill:
    """本体 RAG skill：提供语义检索能力"""

    def __init__(self):
        self.store = None
        if ontology_rag:
            self.store = ontology_rag.VectorStore()
            self.store.load()

    def query_knowledge(self, query: str, top_k: int = 3) -> str:
        """
        语义检索，返回可直接拼进 system prompt 的上下文文本。
        :param query: 用户或专家的查询文本
        :param top_k: 返回前几条
        :return: 格式化后的中文上下文块
        """
        if not self.store:
            return "（技能未就绪：ontology_rag.py 缺失）"
        results = self.store.query(query, top_k)
        if not results:
            return "（未命中相关材料，请基于原有提示词作答）"
        parts = []
        for r in results:
            parts.append(
                f"【来源：{r['meta'].get('source','?')}】\n{r['text']}\n"
            )
        return "\n".join(parts)

    def query_knowledge_json(self, query: str, top_k: int = 3):
        """返回原始 JSON 结果，供高级用法。"""
        if not self.store:
            return []
        return self.store.query(query, top_k)


# WorkBuddy skill 标准接口：skill_main
def skill_main(action: str, params: dict):
    """
    WorkBuddy 标准 skill 入口。
    action: "query_knowledge"
    params: {"query": "...", "top_k": 3}
    """
    skill = OntologyRAGSkill()
    if action == "query_knowledge":
        result = skill.query_knowledge(params.get("query", ""), params.get("top_k", 3))
        return {"success": True, "context": result}
    elif action == "query_knowledge_json":
        result = skill.query_knowledge_json(params.get("query", ""), params.get("top_k", 3))
        return {"success": True, "results": result}
    else:
        return {"success": False, "error": f"未知 action: {action}"}


# 可直接 python -c "import ontology_rag_skill; print(ontology_rag_skill.skill_main('query_knowledge', {'query': '反模式', 'top_k': 2}))"
if __name__ == "__main__":
    # 简单 CLI 测试
    if len(sys.argv) < 2:
        print("用法: python ontology_rag_skill.py \"查询文本\" [top_k]")
        sys.exit(1)
    q = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    print(OntologyRAGSkill().query_knowledge(q, k))