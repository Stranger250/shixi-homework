import os
import sys
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
from hybrid import HybridRetriever
load_dotenv()

# 强制 UTF-8 输出，避免 Windows 终端 GBK 编码无法打印 emoji
sys.stdout.reconfigure(encoding="utf-8")

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

# 本地嵌入模型路径，必须与构建向量库时使用的模型一致
local_model_path = r"D:\models\BAAI-bge-large-zh"

def run_rag_qa(query, persist_directory="./chroma_db"):
    if not os.path.exists(persist_directory):
        print(f"❌ 找不到向量数据库目录 '{persist_directory}'，请先运行 2_vector_builder.py。")
        return

    print("▶ 正在加载嵌入模型...")
    embeddings = HuggingFaceEmbeddings(
        model_name=local_model_path,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    print("▶ 正在加载本地向量数据库...")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key, base_url=base_url)

    system_prompt = (
        "你是一个智能文档问答助手。\n"
        "请严格基于以下提供的文档内容回答用户问题。\n"
        "如果你在文档中找不到答案，请直接说“根据提供的文档，我无法回答该问题”，绝不能凭空编造信息。\n\n"
        "【参考文档内容】\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 混合检索：Embedding 语义检索(权重0.7) + BM25 关键词检索(权重0.3)
    print("▶ 正在初始化混合检索（Embedding + BM25）...")
    retriever = HybridRetriever(vectorstore, alpha=0.7)

    def format_docs(docs):
        return "\n".join(doc.page_content for doc in docs)

    # ==============================
    # ✅ 只检索一次，给打印 + 给LLM用
    # ==============================
    docs = retriever.retrieve(query, k=5)
    
    # 打印分块（附上混合得分构成）
    print("\n" + "="*60)
    print(f"📄 检索到的分块数量：{len(docs)}")
    print("="*60)
    for i, doc in enumerate(docs):
        m = doc.metadata
        print(f"\n--- 分块 {i+1} [混合={m['hybrid_score']} 语义={m['dense_score']} 关键词={m['bm25_score']}] ---")
        print(f"内容：{doc.page_content}")
    print("\n" + "="*60 + "\n")

    # ==============================
    # ✅ 修复：链里直接使用上面检索好的 docs（不再二次检索）
    # ==============================
    rag_chain = (
        {"context": lambda x: format_docs(docs), "input": lambda x: x["input"]}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(f"\n================ 问答测试 ================")
    print(f"👤 用户提问: {query}")
    print("🤖 正在检索知识库并生成答案，请稍候...\n")

    answer = rag_chain.invoke({"input": query})

    print("💡 回答:")
    print(answer)
    print("\n==========================================")

if __name__ == "__main__":
    test_query = "华为2025年的销售收入是多少？研发投入情况如何？"
    run_rag_qa(test_query)