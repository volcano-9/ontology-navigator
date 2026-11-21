#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ontology_rag_inject.py - 本体专家 RAG 自动注入

用法：
  python ontology_rag_inject.py "查询文本" [top_k]
  
输出：system_prompt 片段（命中段落 + 来源），可直接拼进专家的 system prompt 顶部。

示例（在系统提示词前插入）：
  ctx = python ontology_rag_inject.py "身份解析怎么做" 3
  system_prompt = f"【相关上下文】\n{ctx}\n\n【原始提示词】\n{system_prompt}"
"""

import json
import math
import os
import re
import sys
from collections import Counter

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontology_vectorstore.json")


def tokenize(text):
    """中文单字+双字bigram + 英文分词。"""
    text = text.lower()
    tokens = []
    for w in re.findall(r"[a-z0-9]+", text):
        tokens.append(w)
    hanzi = re.findall(r"[\u4e00-\u9fff]", text)
    tokens.extend(hanzi)
    for i in range(len(hanzi) - 1):
        tokens.append(hanzi[i] + hanzi[i + 1])
    return tokens


class VectorStore:
    def __init__(self):
        self.docs = []
        self.df = Counter()
        self.vectors = {}
        self._norm = {}

    def load(self, path=DB_PATH):
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.docs = payload["docs"]
        self.df = Counter(payload["df"])
        self.vectors = payload["vectors"]
        self._norm = {}
        n = len(self.docs)
        for doc_id, tf in self.vectors.items():
            total = sum(tf.values()) or 1
            vec = {}
            for term, c in tf.items():
                idf = math.log(1 + n / (1 + self.df.get(term, 0)))
                vec[term] = (c / total) * idf
            self.vectors[doc_id] = vec
            self._norm[doc_id] = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return True

    def query(self, text, top_k=5):
        q_tf = Counter(tokenize(text))
        q_vec = {}
        total_q = sum(q_tf.values()) or 1
        for term, c in q_tf.items():
            idf = math.log(1 + len(self.docs) / (1 + self.df.get(term, 0)))
            q_vec[term] = (c / total_q) * idf
        q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0

        scores = []
        for doc_id, vec in self.vectors.items():
            dot = sum(v * q_vec.get(t, 0.0) for t, v in vec.items())
            sim = dot / (self._norm[doc_id] * q_norm)
            if sim > 0:
                scores.append((sim, doc_id))
        scores.sort(reverse=True)
        results = []
        for sim, doc_id in scores[:top_k]:
            doc = next(d for d in self.docs if d["id"] == doc_id)
            results.append({"score": round(sim, 4), "id": doc_id,
                            "meta": doc["meta"], "text": doc["text"]})
        return results


def build_context(results):
    """将检索结果拼成中文上下文块。"""
    if not results:
        return "（未命中相关材料，请基于原有提示词作答）"
    parts = []
    for r in results:
        parts.append(
            f"【来源：{r['meta'].get('source','?')}】\n{r['text']}\n"
        )
    return "\n".join(parts)


def main():
    if len(sys.argv) < 2:
        print("用法: python ontology_rag_inject.py \"查询文本\" [top_k]")
        return
    q = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    store = VectorStore()
    if not store.load():
        print("向量库不存在，请先运行 python ontology_rag.py index <目录>")
        return
    results = store.query(q, k)
    print(build_context(results))


if __name__ == "__main__":
    main()