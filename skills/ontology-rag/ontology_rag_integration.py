"""
ontology_rag_integration.py - 向量库升级插槽

当前方案：Pure Python TF-IDF（零依赖，不需外网）
若要换真 embedding（Chroma / OpenAI / 混元），仅需：

1. 在此文件最开尾的 VectorStore 类里，将 `self.embed(text)` 方法改为调用真 embedding 模型。
2. 保持 `query()` 的其余代码不变——只依赖 `self.vectors[doc_id]` 与 `self._norm[doc_id]`。

此处给出三种常用 embedding 驱动的替换示例，仅作演示，实际使用请自行安装对应库。

示例 A：ChromaDB（需 pip install chromadb）
示例 B：OpenAI embedding（需设 OPENAI_API_KEY）
示例 C：百混元 embedding（通过 http 接口）
"""

import json
import math
import os
import re
import sys
from collections import Counter

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontology_vectorstore.json")


# ---------- 1. 原始 TF-IDF 实现（当前方案） ----------
def tokenize(text):
    """中文 bigram+单字 + 英文分词。"""
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

    def add(self, doc_id, text, meta=None):
        if doc_id in self.vectors:
            self._remove(doc_id)
        self.docs.append({"id": doc_id, "text": text, "meta": meta or {}})
        tf = Counter(tokenize(text))
        for term in set(tf):
            self.df[term] += 1
        self.vectors[doc_id] = tf
        self._recompute_tfidf(doc_id)

    def _remove(self, doc_id):
        self.docs = [d for d in self.docs if d["id"] != doc_id]
        tf = self.vectors.pop(doc_id, None)
        if tf:
            for term in tf:
                self.df[term] -= 1
                if self.df[term] <= 0:
                    del self.df[term]

    def _recompute_tfidf(self, doc_id):
        n = len(self.docs)
        tf = self.vectors[doc_id]
        total = sum(tf.values()) or 1
        vec = {}
        for term, c in tf.items():
            idf = math.log(1 + n / (1 + self.df.get(term, 0)))
            vec[term] = (c / total) * idf
        self.vectors[doc_id] = vec
        self._norm[doc_id] = math.sqrt(sum(v * v for v in vec.values())) or 1.0

    def _remove_all_norms(self):
        self._norm = {}

    def _recompute_all(self):
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
                            "meta": doc["meta"], "text": doc["text"][:300]})
        return results


# ---------- 2. 真 embedding 驱动的查询（插槽入口） ----------
# 思路：把“文本 → 向量”抽象成 `self.embed(text)`，当前默认返回 TF-IDF 向量。
# 子类或 monkey-patch 即可改成真 embedding。

class EmbeddingVectorStore(VectorStore):
    """
    子类：若想用 Chroma / OpenAI embedding，请继承此类并重写 `embed()` 即可。
    其余 query()/add()/save()/load() 完全不变。
    """

    def embed(self, text):
        """
        默认返回 TF-IDF 向量（与父类 VectorStore.query 兼容）。
        子类重写此函数，返回 dict(token_id -> float) 形式的向量。

        例如：
        # 用 OpenAI:
        #   import openai
        #   resp = openai.Embedding.create(model="text-embedding-3-small", input=text)
        #   return {f"token_{i}": v for i, v in enumerate(resp['data'][0]['embedding'])}
        # 用 Chroma:
        #   return chroma_client.embed(text, model="all-MiniLM-L6-v2")
        # 当前默认：退回 TF-IDF
        return self._tfidf_embed(text)

    def _tfidf_embed(self, text):
        """把文本转成 TF-IDF 向量 dict（键为词，值为权重）"""
        tokens = tokenize(text)
        tf = Counter(tokens)
        n = len(self.docs) or 1
        vec = {}
        for term in set(tokens):
            idf = math.log(1 + n / (1 + self.df.get(term, 0)))
            vec[term] = (tf[term] / max(sum(tf.values()), 1)) * idf
        return vec


# ---------- 保持向下兼容，main 入口仍用原 VectorStore ----------
# 如果想测试真 embedding，可手动改用 EmbeddingVectorStore


# ---------- 3. RAG 自动注入工具 ----------
# 使用示例：
# from ontology_rag_integration import EmbeddingVectorStore
# store = EmbeddingVectorStore()
# store.load()
# # 查询并把结果拼进系统提示词
# results = store.query("Palantir 本体反模式", top_k=3)
# context = "\n\n".join([r["text"] for r in results])
# prompt = f"""以下是相关资料：
# {context}
# 
# 基于上述资料，回答用户问题。"""
# 这样即可实现 RAG 增强。

# ---------- 4. CLI（保持不变，仍跑 TF-IDF） ----------
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    store = VectorStore()  # 若改成 EmbeddingVectorStore，query 效果会变
    store.load()

    if cmd == "index":
        if len(sys.argv) < 3:
            print("用法: python ontology_rag.py index <目录或文件>")
            return
        target = sys.argv[2]
        n = index_path(store, target, base=os.path.dirname(os.path.abspath(target)))
        store.save()
        print(f"已索引 {n} 个文本块，当前共 {len(store.docs)} 块，来源 {len(store.docs)} 份文档片段")

    elif cmd == "query":
        if len(sys.argv) < 3:
            print("用法: python ontology_rag.py query "查询文本" [top_k]")
            return
        q = sys.argv[2]
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        results = store.query(q, k)
        if not results:
            print("未命中。")
            return
        for r in results:
            print(f"\n[{r['score']}] {r['id']}")
            print("   " + r["text"].replace("\n", " ")[:200])

    elif cmd == "stats":
        print(f"文档块数: {len(store.docs)}")
        print(f"词表大小: {len(store.df)}")
        if store.docs:
            sources = sorted({d['meta'].get('source', '?') for d in store.docs})
            print("来源文件:")
            for s in sources:
                print("  -", s)

    elif cmd == "reset":
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        print("向量库已清空。")

    else:
        print(__doc__)


if __name__ == "__main__":
    main()