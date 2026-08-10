"""
混合检索器（Hybrid Retriever）

融合两种检索方式，兼顾"语义理解"与"关键词精确匹配"：
1. 稠密检索（Dense）：bge-large-zh 向量 + Chroma 相似度检索 → 理解语义（如"销售收入"≈"营业额"）
2. 稀疏检索（Sparse）：BM25 关键词打分（jieba 中文分词）→ 精确匹配专有名词（如"研发费用""JVM"）

融合公式：final = alpha * dense_score + (1 - alpha) * bm25_score
默认权重 alpha=0.7（语义为主），BM25 占 0.3（关键词为辅）：
- 语义检索是主力，能召回"意思相近但字面不同"的文本
- BM25 补充精确词命中，财报里的数字/专有名词按关键词也能搜到
"""

import sys

import jieba
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

# 强制 UTF-8 输出，避免 Windows 终端 GBK 编码无法打印 emoji
sys.stdout.reconfigure(encoding="utf-8")


class HybridRetriever:
    def __init__(self, vectorstore, alpha=0.7, pool_k=30):
        """
        vectorstore: 已建好的 Chroma 向量库
        alpha: 稠密（语义）检索权重；(1-alpha) 为 BM25（关键词）检索权重
        pool_k: 两个渠道各自先取前 pool_k 个候选，再合并去重后融合排序
        """
        self.vectorstore = vectorstore
        self.alpha = alpha
        self.pool_k = pool_k

        # 从向量库取回所有分块原文，构建 BM25 关键词索引
        print("▶ 正在构建 BM25 关键词索引...")
        data = vectorstore._collection.get(include=["documents"])
        self.documents = data["documents"]
        self.bm25 = BM25Okapi([self._tokenize(d) for d in self.documents])
        print(f"✅ BM25 索引构建完成，共 {len(self.documents)} 个文本块")

    @staticmethod
    def _tokenize(text):
        """jieba 中文分词（cut_for_search 搜索模式，召回更多词）"""
        return list(jieba.cut_for_search(text))

    @staticmethod
    def _minmax_norm(values):
        """线性归一化到 [0, 1]（BM25 原始分数无上界，需归一化后才能与相似度加权）"""
        if not values:
            return []
        vmin, vmax = min(values), max(values)
        if vmax - vmin < 1e-9:
            return [1.0] * len(values)
        return [(v - vmin) / (vmax - vmin) for v in values]

    def retrieve(self, query, k=5):
        """混合检索：返回 top-k 的 Document 列表（metadata 带三个得分）"""
        q_tokens = self._tokenize(query)

        # ---- 1. 稠密检索：Embedding 语义相似度 ----
        dense_hits = self.vectorstore.similarity_search_with_relevance_scores(query, k=self.pool_k)
        dense_map = {doc.page_content: score for doc, score in dense_hits}

        # ---- 2. 稀疏检索：BM25 关键词打分（分数与 self.documents 顺序一一对应）----
        bm25_raw = self.bm25.get_scores(q_tokens)
        top_bm_idx = sorted(range(len(bm25_raw)), key=lambda i: bm25_raw[i], reverse=True)[:self.pool_k]
        bm25_map = {self.documents[i]: bm25_raw[i] for i in top_bm_idx}

        # ---- 3. 归一化后加权融合 ----
        # 稠密分数（relevance）本身在 0~1 之间，直接使用；BM25 分数做 min-max 归一化
        bm25_norm_map = dict(zip(bm25_map.keys(), self._minmax_norm(list(bm25_map.values()))))

        candidates = set(dense_map.keys()) | set(bm25_map.keys())  # 两渠道候选的并集
        results = []
        for text in candidates:
            d = dense_map.get(text, 0.0)      # 只在 BM25 命中的，语义分记 0
            b = bm25_norm_map.get(text, 0.0)  # 只在语义命中的，关键词分记 0
            fused = self.alpha * d + (1 - self.alpha) * b
            results.append((text, fused, d, b))

        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:k]

        # 包装成 Document 对象，方便下游 format_docs / prompt 直接使用
        docs = []
        for text, fused, d, b in results:
            doc = Document(
                page_content=text,
                metadata={
                    "hybrid_score": round(fused, 4),
                    "dense_score": round(d, 4),
                    "bm25_score": round(b, 4),
                },
            )
            docs.append(doc)
        return docs


if __name__ == "__main__":
    # 单独测试混合检索（不调用 LLM）
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma

    embeddings = HuggingFaceEmbeddings(
        model_name=r"D:\models\BAAI-bge-large-zh",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vs = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    retriever = HybridRetriever(vs, alpha=0.7)
    for q in ["华为2025年的销售收入是多少？研发投入情况如何？", "员工的年假有多少天？"]:
        print("\n" + "=" * 60)
        print(f"查询: {q}")
        print("=" * 60)
        for i, d in enumerate(retriever.retrieve(q, k=5), 1):
            m = d.metadata
            print(f"\nTop{i} [混合={m['hybrid_score']} 语义={m['dense_score']} 关键词={m['bm25_score']}]")
            print(d.page_content[:80].replace("\n", " "))
