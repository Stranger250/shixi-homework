from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import importlib
import os
import shutil
import sys

# 强制 UTF-8 输出，避免 Windows 终端 GBK 编码无法打印 emoji
sys.stdout.reconfigure(encoding="utf-8")

# 动态导入避免模块名以数字开头带来的语法错误
pdf_loader = importlib.import_module("1_pdf_loader")
load_and_split_pdfs = pdf_loader.load_and_split_pdfs

def build_vector_store(docs_dir="./docs", persist_directory="./chroma_db"):
    """
    负责调用文本分割函数，并使用本地 BAAI/bge-large-zh 进行向量化，最后保存到本地 Chroma 数据库
    """
    # 0. 重建前删除旧的向量库，避免分块重复追加（Chroma.from_documents 是追加而非覆盖）
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"🗑 已删除旧向量库目录: {persist_directory}")

    # 1. 获取分割后的文档块
    split_docs = load_and_split_pdfs(docs_dir)
    if not split_docs:
        print("构建终止：没有可用的文档块。")
        return None

    # 2. 加载本地 BGE 嵌入模型（bge-large-zh，向量维度 1024）
    print("▶ 正在加载本地 BGE 嵌入模型...")
    # 针对 BGE 模型，官方推荐使用 HuggingFaceBgeEmbeddings 并开启 normalize_embeddings
    model_name = r"D:\models\BAAI-bge-large-zh"

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cuda'}, # 如果有GPU可改为 'cuda'
        encode_kwargs={'normalize_embeddings': True} # BGE 模型必须开启标准化
    )
    
    # 3. 向量化并存储到 Chroma
    print(f"▶ 正在将文本向量化并存储到 Chroma 数据库 ({persist_directory})...")
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print("✅ 向量数据库构建完成并已持久化保存！")
    return vectorstore

if __name__ == "__main__":
    # 运行此脚本以构建向量库
    vs = build_vector_store()

        # ===================== 查看 embedding 是否成功 =====================
    print("\n" + "="*50)
    print("📊 向量库统计信息：")
    print("文档分块总数：", vs._collection.count())
    print("="*50)
