"""
随堂任务1：Embedding 模型测试与向量相似度计算

功能：
1. 用 BAAI/bge-small-zh-v1.5 编码 5 个招聘相关句子，输出向量维度与前 5 个数值
2. 计算 5 个句子两两之间的余弦相似度，输出 5x5 矩阵，找出最相似的句子对
3. 实战问答：计算用户问题与 5 个句子的相似度，返回最相似的 Top 2，并拼接生成回答
"""

import os
import sys
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 强制 UTF-8 输出，避免 Windows 终端 GBK 编码无法打印 emoji
sys.stdout.reconfigure(encoding="utf-8")

# 配置 HuggingFace 国内镜像加速下载（若已设置环境变量则优先使用，
# 遇到 hf-mirror 无法下载时可改为官方源: set HF_ENDPOINT=https://huggingface.co）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from langchain_huggingface import HuggingFaceEmbeddings

# ===================== 1. 待测试的 5 个句子 =====================
sentences = [
    "Java开发工程师要求3年以上经验",
    "Python岗位要求熟悉Django框架",
    "公司节日福利包括购物卡和电影票",
    "员工享受带薪年假和五险一金",
    "Java高级工程师需精通JVM调优",
]

question = "Java岗位有什么要求？"

# 本地已下载的 BGE 嵌入模型路径（bge-large-zh，向量维度 1024）
MODEL_NAME = r"D:\models\BAAI-bge-large-zh"


def load_embeddings():
    """加载 HuggingFace BGE 嵌入模型（BGE 模型必须开启 normalize_embeddings）"""
    print(f"▶ 正在加载本地嵌入模型: {MODEL_NAME} ...")
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},          # 有 GPU 可改为 'cuda'
        encode_kwargs={"normalize_embeddings": True},
    )


def main():
    embeddings = load_embeddings()

    # ===================== 任务1: 句子向量表示 =====================
    print("\n" + "=" * 60)
    print("📊 任务1：5 个句子的向量表示")
    print("=" * 60)
    vecs = np.array(embeddings.embed_documents(sentences))
    for i, (s, v) in enumerate(zip(sentences, vecs), 1):
        print(f"\n句子{i}: {s}")
        print(f"  向量维度: {v.shape[0]}")
        print(f"  前5个数值: {np.round(v[:5], 6)}")

    # ===================== 任务2: 两两余弦相似度 =====================
    print("\n" + "=" * 60)
    print("📐 任务2：句子两两余弦相似度矩阵 (5x5)")
    print("=" * 60)
    sim_matrix = cosine_similarity(vecs)
    np.set_printoptions(precision=4, suppress=True)
    print(sim_matrix)

    # 找出最相似的句子对（排除自身）
    best_pair, best_score = None, -1.0
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            if sim_matrix[i][j] > best_score:
                best_pair, best_score = (i, j), sim_matrix[i][j]
    print(f"\n🏆 最相似的句子对: ")
    print(f"  句子{best_pair[0]+1}: {sentences[best_pair[0]]}")
    print(f"  句子{best_pair[1]+1}: {sentences[best_pair[1]]}")
    print(f"  相似度: {best_score:.4f}")

    # ===================== 任务3: 实战问答（检索 Top2 + 生成回答） =====================
    print("\n" + "=" * 60)
    print("🎯 任务3：用户问答相似度 Top 2")
    print("=" * 60)
    print(f"用户提问: {question}")
    q_vec = np.array(embeddings.embed_query(question))
    q_sim = cosine_similarity(q_vec.reshape(1, -1), vecs)[0]

    # 按相似度降序排序，取 Top 2
    top2_idx = np.argsort(q_sim)[::-1][:2]
    print("\n所有句子的相似度:")
    for i in range(len(sentences)):
        print(f"  {q_sim[i]:.4f}  {sentences[i]}")
    print("\n🏅 最相似的 Top 2:")
    for rank, i in enumerate(top2_idx, 1):
        print(f"  Top{rank}: {sentences[i]}  (相似度 {q_sim[i]:.4f})")

    # 规则拼接 Top 2 句子，生成一段直接回答（无需 LLM/API）
    answer = "；".join(f"{rank}) {sentences[i]}" for rank, i in enumerate(top2_idx, 1))
    print(f"\n💡 回答（规则拼接 Top 2 检索结果）: {question} → {answer}")


if __name__ == "__main__":
    main()
