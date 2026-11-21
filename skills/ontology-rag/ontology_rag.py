"""
ontology_rag.py - 本体领航员专用本地向量库（零依赖）

特性：
- 纯 Python 实现，无需联网、无需 pip install
- 中文双字 gram + 英文分词，TF-IDF 向量，余弦相似度检索
- 持久化为 JSON，随时 load 恢复
- 预留 embed() 接口：接入 Chroma / OpenAI embedding 时只需替换该函数

用法：
  python ontology_rag.py index <目录或文件>   # 建库/追加
  python ontology_rag.py query "查询文本" [top_k]
  python ontology_rag.py stats                # 查看库状态
"""

import json
import math
import os
import re
import sys
from collections import Counter

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontology_vectorstore.json")

# ---------- 分词 ----------

def tokenize(text):
    """中文按 bigram+单字，英文按单词小写。"""
    text = text.lower()
    tokens = []
    # 英文单词
    for w in re.findall(r"[a-z0-9]+", text):
        tokens.append(w)
    # 中文：单字 + 双字 bigram
    hanzi = re.findall(r"[\u4e00-\u9fff]", text)
    tokens.extend(hanzi)
    for i in range(len(hanzi) - 1):
        tokens.append(hanzi[i] + hanzi[i + 1])
    return tokens


# ---------- 向量化 ----------

class VectorStore:
    def __init__(self):
        self.docs = []          # [{id, text, meta}]
        self.df = Counter()     # 词 -> 文档频率
        self.vectors = {}       # id -> {token: tfidf}
        self._norm = {}         # id -> 向量模长

    # ----- 索引 -----

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

    def _recompute_all(self):
        self._norm = {}
        n = len(self.docs)
        for doc_id, tf in self.vectors.items():
            vec = {}
            for term, c in tf.items():
                idf = math.log(1 + n / (1 + self.df.get(term, 0)))
                vec[term] = (c / total(tf)) * idf
            self.vectors[doc_id] = vec
            self._norm[doc_id] = math.sqrt(sum(v * v for v in vec.values())) or 1.0

    # ----- 检索 -----

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

    # ----- 持久化 -----

    def save(self, path=DB_PATH):
        payload = {"docs": self.docs,
                   "df": dict(self.df),
                   "vectors": {k: v for k, v in self.vectors.items()}}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

    def load(self, path=DB_PATH):
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.docs = payload["docs"]
        self.df = Counter(payload["df"])
        self.vectors = payload["vectors"]
        self._recompute_all()
        return True


def total(tf):
    return sum(tf.values()) or 1


# ---------- 文档采集 ----------

SUPPORTED_EXT = {".md", ".yaml", ".yml", ".csv", ".txt", ".json"}

def iter_files(path):
    if os.path.isfile(path):
        yield path
    else:
        for root, _, files in os.walk(path):
            for fn in sorted(files):
                if os.path.splitext(fn)[1].lower() in SUPPORTED_EXT:
                    yield os.path.join(root, fn)


def chunk_text(text, max_len=600):
    """按段落切，每块不超过 max_len 字符。"""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 > max_len and cur:
            chunks.append(cur)
            cur = p
        else:
            cur = (cur + "\n\n" + p) if cur else p
    if cur:
        chunks.append(cur)
    return chunks or [text[:max_len]]


def index_path(store, path, base=""):
    count = 0
    for fpath in iter_files(path):
        rel = os.path.relpath(fpath, base) if base else fpath
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        ext = os.path.splitext(fpath)[1].lower()
        if ext == ".csv":
            content = _csv_to_text(content)
        for i, chunk in enumerate(chunk_text(content)):
            doc_id = f"{rel}#{i}"
            store.add(doc_id, chunk, {"source": rel, "chunk": i, "ext": ext})
            count += 1
    return count


def _csv_to_text(content):
    lines = [l for l in content.splitlines() if l.strip()]
    if not lines:
        return ""
    header = [h.strip() for h in lines[0].split(",")]
    out = [" | ".join(header)]
    for l in lines[1:]:
        out.append(" | ".join(c.strip() for c in l.split(",")))
    return "\n".join(out)


# ---------- CLI ----------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    store = VectorStore()
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
            print("用法: python ontology_rag.py query \"查询文本\" [top_k]")
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
