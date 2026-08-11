import os
from langchain_community.document_loaders import DirectoryLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split_pdfs(docs_dir="./docs"):
    """
    负责从指定目录加载所有 PDF 文件，并将其切分为文本块
    """
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"提示: 已自动创建 '{docs_dir}' 文件夹，请将5个 PDF 文件放入该文件夹后重新运行。")
        return []

    print(f"▶ 正在从 [{docs_dir}] 文件夹批量加载 PDF 文件...")
    # 使用 DirectoryLoader 配合 PDFPlumberLoader 批量加载
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.pdf",
        loader_cls=PDFPlumberLoader
    )
    documents = loader.load()
    
    if not documents:
        print(f"提示: '{docs_dir}' 文件夹中没有找到 PDF 文件，请放入文件后重试。")
        return []
        
    print(f"✅ 成功加载文档，共提取 {len(documents)} 页内容。")

    print("▶ 正在进行文本分割...")
    # 分块策略说明（适配华为年报这类长中文财报）：
    # 1. chunk_size=500：与 bge-large-zh 的 512 token 上限匹配（中文约1字≈1 token），避免截断
    # 2. chunk_overlap=80：块间重叠，保持上下文连贯，避免关键信息恰好被切在边界
    # 3. separators 加入中文标点：优先在段落/完整句子的边界切分，避免把语义拆碎
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"✅ 文档已成功分割为 {len(split_docs)} 个文本块。")
    avg_len = sum(len(d.page_content) for d in split_docs) / len(split_docs)
    print(f"📏 平均每个文本块长度：{avg_len:.0f} 字符")
    print(split_docs[0].page_content)
    print("-----------------")
    print(split_docs[1].page_content)
    
    return split_docs

if __name__ == "__main__":
    # 测试运行该文件
    docs = load_and_split_pdfs()
