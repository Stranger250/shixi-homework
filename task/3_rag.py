"""
task3/3_rag.py — 升阶 RAG：稠密检索 + 稀疏检索 RRF 融合 + 本地 Reranker 精排

基于基础 RAG 流程（1_pdf_loader 拆块 → 2_vector_builder 建库 → 本文件检索问答）的优化：

  ① 双路召回（粗排）：
      稀疏 BM25 关键词召回（jieba 分词，精确匹配专有名词）
      稠密 Embedding 语义召回（bge-large-zh，理解"意思相近但字面不同"）
  ② RRF 融合：
      Reciprocal Rank Fusion，score = Σ 1/(k + rank)
      只看两个渠道的"排名"而非原始分数，天然免调权重
  ③ Reranker 精排：
      本地 bge-reranker-base 对 (query, 每个分块) 逐对打分，
      把最相关的分块排到最前，过滤掉误召回
  ④ 检索增强生成：
      把精排后的分块拼进提示词，由大模型（.env 配置的 ChatOpenAI）生成回答

模型均从本地加载：
  local_embed  = D:\\models\\BAAI-bge-large-zh
  local_rerank = D:\\models\\BAAI-bge-reranker-base
"""

import os
import sys

import jieba
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from dotenv import load_dotenv

# 强制 UTF-8 输出，避免 Windows 终端 GBK 编码无法打印 emoji
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

# ===================== 配置 =====================
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

RRF_K = 60          # RRF 常数 k：越大，排名差异的影响越平缓（业界常用 60）
TOP_K = 8           # 粗排：每个渠道各召回多少条
FINAL_TOP_K = 5     # RRF 融合后（精排前）保留多少条
RERANK_TOP_K = 3    # 精排后最终输出多少条

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
local_embed_path = r"D:\models\BAAI-bge-large-zh"
local_rerank_path = r"D:\models\BAAI-bge-reranker-base"


# ===================== 本地 Reranker（精排） =====================
class LocalReranker:
    """基于 BGE-Reranker 的交叉编码器重排序：对 (query, 文档) 逐对打分"""

    def __init__(self, model_path):
        print(f"▶ 正在加载本地 Reranker: {model_path} (device={DEVICE})...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(DEVICE)
        self.model.eval()

    def rank(self, query, docs):
        """返回 (按重排分降序的 docs, 对应的分数列表)"""
        pairs = [[query, doc.page_content] for doc in docs]
        with torch.no_grad():
            inputs = self.tokenizer(
                pairs, padding=True, truncation=True,
                return_tensors="pt", max_length=512
            )
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
            scores = self.model(**inputs, return_dict=True).logits.view(-1).float().tolist()
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [d for d, _ in ranked], [s for _, s in ranked]


# 全局加载一次（避免每次问答重复加载模型）
reranker = LocalReranker(local_rerank_path)


# ===================== 工具函数 =====================
def get_all_docs(vectorstore):
    """从向量库取出全部分块原文，用于构建 BM25 索引"""
    from langchain_core.documents import Document
    data = vectorstore.get(include=["documents", "metadatas"])
    return [Document(page_content=d, metadata=m if m else {})
            for d, m in zip(data["documents"], data["metadatas"])]


def jieba_tokenize(text):
    """jieba 中文分词（search 模式，召回更多词）"""
    return list(jieba.cut_for_search(text))


def short(doc, n=55):
    """截断打印内容，避免刷屏"""
    return doc.page_content.replace("\n", " ")[:n]


def format_docs(docs):
    return "\n".join(x.page_content for x in docs)


# ===================== ① 双路召回（粗排） =====================
def dual_recall(query, vectorstore, all_docs):
    """BM25 关键词召回 + Embedding 语义召回，各取 TOP_K 条"""
    print("\n▶ 粗排①：BM25 关键词召回...")
    # 注意：参数是 preprocess_func（中文必须用 jieba 分词，否则默认按空格切分会失效）
    bm25_retriever = BM25Retriever.from_documents(all_docs, preprocess_func=jieba_tokenize)
    bm25_retriever.k = TOP_K
    bm25_docs = bm25_retriever.invoke(query)

    print("▶ 粗排②：Embedding 语义召回...")
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    vector_docs = vector_retriever.invoke(query)

    # 打印粗排结果
    print("\n" + "=" * 72)
    print("🔍 粗排结果（融合前）")
    print("=" * 72)
    print(f"\n--- ① BM25 关键词召回（Top {TOP_K}）---")
    for i, d in enumerate(bm25_docs, 1):
        print(f"  {i:>2}. {short(d)}")
    print(f"\n--- ② Embedding 语义召回（Top {TOP_K}）---")
    for i, d in enumerate(vector_docs, 1):
        print(f"  {i:>2}. {short(d)}")

    return bm25_docs, vector_docs


# ===================== ② RRF 融合 =====================
def fuse_rrf(bm25_docs, vector_docs, top_k=FINAL_TOP_K, k=RRF_K):
    """RRF（Reciprocal Rank Fusion）：
    score = Σ 1/(k + rank)，同一文档在两个渠道的排名越好，融合分越高。
    只看排名不看原始分数，因此两个渠道不用统一量纲、无需调权重。"""
    rrf = {}
    for docs in (vector_docs, bm25_docs):
        for rank, d in enumerate(docs, 1):
            rrf[d.page_content] = rrf.get(d.page_content, 0.0) + 1.0 / (k + rank)
    ranked = sorted(rrf.items(), key=lambda x: x[1], reverse=True)
    doc_map = {d.page_content: d for d in bm25_docs + vector_docs}
    return [doc_map[c] for c, _ in ranked[:top_k]], dict(ranked)


# ===================== ③ 精排 + ④ 生成 主流程 =====================
def retrieve_and_rerank(query, vectorstore):
    """完整检索链路：双路召回 → RRF 融合 → Reranker 精排，返回最终分块"""
    all_docs = get_all_docs(vectorstore)
    bm25_docs, vector_docs = dual_recall(query, vectorstore, all_docs)

    # RRF 融合
    fused_docs, rrf_scores = fuse_rrf(bm25_docs, vector_docs)
    print("\n" + "=" * 72)
    print(f"📊 RRF 融合（k={RRF_K}）→ 取 Top {len(fused_docs)}（精排前）")
    print("=" * 72)
    for i, d in enumerate(fused_docs, 1):
        print(f"  {i:>2}. [RRF分={rrf_scores[d.page_content]:.4f}] {short(d)}")

    # Reranker 精排
    print("\n" + "=" * 72)
    print("🎯 Reranker 精排（bge-reranker-base，逐对打分重排）")
    print("=" * 72)
    reranked_docs, reranked_scores = reranker.rank(query, fused_docs)
    for i, (d, s) in enumerate(zip(reranked_docs, reranked_scores), 1):
        mark = "★" if i <= RERANK_TOP_K else " "
        print(f"  {mark}{i:>2}. [重排分={s:.4f}] {short(d)}")

    return reranked_docs[:RERANK_TOP_K]


def run_rag_qa(query, persist_directory="./chroma_db"):
    if not os.path.exists(persist_directory):
        print("❌ 找不到向量数据库，请先运行 2_vector_builder.py。")
        return

    print(f"▶ 正在加载本地 Embedding 模型: {local_embed_path} (device={DEVICE})...")
    embeddings = HuggingFaceEmbeddings(
        model_name=local_embed_path,
        model_kwargs={"device": DEVICE},
        encode_kwargs={"normalize_embeddings": True}
    )
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    # 检索：双路召回 → RRF 融合 → Reranker 精排
    final_docs = retrieve_and_rerank(query, vectorstore)
    print(f"\n✅ 检索完成，精排后 {len(final_docs)} 条分块将交给 LLM 生成回答")

    # 生成：精排结果 + 提示词 → 大模型回答
    llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key, base_url=base_url)

    system_prompt = (
        "你是一个智能文档问答助手。\n"
        "请严格基于以下提供的文档内容回答用户问题。\n"
        "如果找不到答案，请直接说“根据提供的文档，我无法回答该问题”，不要编造。\n\n"
        "【参考文档】\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    rag_chain = (
        {"context": lambda x: format_docs(final_docs), "input": lambda x: x["input"]}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("\n================ 问答 ================")
    print(f"👤 问题：{query}")
    answer = rag_chain.invoke({"input": query})
    print(f"💡 回答：\n{answer}")
    print("=" * 60)


if __name__ == "__main__":
    run_rag_qa("节日和生日福利有什么？")
