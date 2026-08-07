import os
import re
import asyncio
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

# 1. 加载环境变量
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

# 2. 初始化大模型
llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.7
)
# 临时弄一个低温度的模型给主管用，保证他回答严谨
supervisor_llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.1
)

VALID_DEPARTMENTS = ["destination", "budget", "transportation", "food", "culture"]

# ==========================================
# 第一步：定义各个顾问节点 (Chains)
# ==========================================
# 1. 主管节点 (分发任务)
# 注意：我们要求主管只输出 destination、budget、transportation、food、culture、 或 unknown
supervisor_prompt = ChatPromptTemplate.from_template(
    "你是一个旅游公司的项目主管。请根据客户的问题：【{question}】，决定由一个或多个顾问来回答。\n"
    "你只能从以下几个词中选择输出，可选择一个或多个（多个用英文逗号分隔）：\n"
    "1. destination（如果问题关于目的地）\n"
    "2. budget（如果问题关于预算）\n"
    "3. transportation（如果问题关于交通方式）\n"
    "4. food（如果问题关于美食）\n"
    "5. culture（如果问题关于文化活动）\n"
    "6. unknown（如果不属于以上问题）\n"
    "只输出顾问名，不要输出其他任何内容。你的输出："
)


def parse_departments(raw: str) -> list:
    """把主管的输出解析成顾问名列表；无合法顾问时返回 ['unknown']"""
    raw = (raw or "").strip().lower()
    parts = [p.strip() for p in re.split(r"[,，、\s]+", raw) if p.strip()]
    deps = [p for p in parts if p in VALID_DEPARTMENTS]
    return deps if deps else ["unknown"]


# 这里用 lower() 确保输出一定是小写，方便后面做判断
supervisor_chain = supervisor_prompt | supervisor_llm | StrOutputParser() | parse_departments

# 2. 目的地顾问
destination_prompt = ChatPromptTemplate.from_template("你是一个目的地顾问，请用不超过50个字解答：{question}")
destination_chain = destination_prompt | llm | StrOutputParser() | (lambda x: f"【目的地顾问回复】 {x}")

# 3. 预算顾问
budget_prompt = ChatPromptTemplate.from_template("你是一个预算顾问，请用不超过50个字解答：{question}")
budget_chain = budget_prompt | llm | StrOutputParser() | (lambda x: f"【预算顾问回复】 {x}")

# 4. 交通顾问
transportation_prompt = ChatPromptTemplate.from_template("你是一个交通顾问，请用不超过50个字解答：{question}")
transportation_chain = transportation_prompt | llm | StrOutputParser() | (lambda x: f"【交通顾问回复】 {x}")

# 5. 美食顾问
food_prompt = ChatPromptTemplate.from_template("你是一个美食顾问，请用不超过50个字解答：{question}")
food_chain = food_prompt | llm | StrOutputParser() | (lambda x: f"【美食顾问回复】 {x}")

# 6. 文化顾问
culture_prompt = ChatPromptTemplate.from_template("你是一个文化顾问，请用不超过50个字解答：{question}")
culture_chain = culture_prompt | llm | StrOutputParser() | (lambda x: f"【文化顾问回复】 {x}")

# 7. 未知问题
unknown_chain = (lambda x: "【客服回复】 您好，我们是一家旅游公司，您的问题超出了我们的服务范围。")

CHAIN_MAP = {
    "destination": destination_chain,
    "budget": budget_chain,
    "transportation": transportation_chain,
    "food": food_chain,
    "culture": culture_chain,
}


# ==========================================
# 多顾问并发异步函数
# ==========================================
async def get_multi_answer(question: str, departments: list) -> str:
    """并发调用指定的多个顾问，合并各顾问的回答"""
    # 异步并行发起多个LLM请求
    tasks = [
        CHAIN_MAP[d].ainvoke({"question": question})
        for d in departments
        if d in CHAIN_MAP
    ]
    # 等待所有任务完成
    results = await asyncio.gather(*tasks)
    # 拼接各顾问结果统一返回
    return "=====多顾问并发联合回答=====\n" + "\n".join(results)


async def generate_travel_plan(destination: str, days: int, budget: float) -> str:
    """用户输入目的地+天数+预算，自动调用全部 5 个顾问生成完整旅行计划"""
    question = f"我计划去{destination}旅行{days}天，总预算{budget}元，请给出建议"
    result = await get_multi_answer(question, VALID_DEPARTMENTS)
    return f"=====完整旅行计划（{destination} {days}天 预算{budget}元）=====\n" + result


# ==========================================
# 第二步：组装纯 LangChain 的条件路由 (RunnableBranch)
# ==========================================
# 输入格式：{"question": "用户问题", "mode": "single"/"multi"}
context_chain = {
    "question": (lambda x: x["question"]),
    "mode": (lambda x: x["mode"]),
    "departments": supervisor_chain,
}

# 分支优先级：先判断mode，再判断部门
routing_branch = RunnableBranch(
    # 分支1：并发多顾问模式
    (lambda x: x["mode"] == "multi" and "unknown" not in x["departments"],
     lambda x: asyncio.run(get_multi_answer(x["question"], x["departments"]))
     ),
    # 分支2：单顾问模式 - 目的地问题
    (lambda x: x["mode"] == "single" and x["departments"] == ["destination"],
     lambda x: destination_chain.invoke({"question": x["question"]})
     ),
    # 分支3：单顾问模式 - 预算问题
    (lambda x: x["mode"] == "single" and x["departments"] == ["budget"],
     lambda x: budget_chain.invoke({"question": x["question"]})
     ),
    # 分支4：单顾问模式 - 交通问题
    (lambda x: x["mode"] == "single" and x["departments"] == ["transportation"],
     lambda x: transportation_chain.invoke({"question": x["question"]})
     ),
    # 分支5：单顾问模式 - 美食问题
    (lambda x: x["mode"] == "single" and x["departments"] == ["food"],
     lambda x: food_chain.invoke({"question": x["question"]})
     ),
    # 分支6：单顾问模式 - 文化问题
    (lambda x: x["mode"] == "single" and x["departments"] == ["culture"],
     lambda x: culture_chain.invoke({"question": x["question"]})
     ),
    # 兜底分支：未知问题统一走客服
    (lambda x: unknown_chain(x))
)

# 最终把上下文链路 + 路由分支拼接
final_pipeline = context_chain | routing_branch


def run(question: str, mode: str) -> str:
    departments = supervisor_chain.invoke({"question": question})
    print(f"🎯 主管分发决策：{departments}")
    return final_pipeline.invoke({"question": question, "mode": mode})


# 第三步：运行测试
def main():
    print("🚀 旅游规划智能分发系统测试\n")

    # 测试用例列表：(提问, 运行模式)
    test_cases = [
        ("第一次去东京，哪些地方值得去？", "single"),
        ("去泰国玩一周预算多少合适？", "single"),
        ("去重庆自由行怎么安排交通？", "single"),
        ("广州有什么必吃美食？", "single"),
        ("去敦煌应该了解哪些历史文化？", "single"),
        ("2+2等于几？", "single"),
        ("去成都玩，要推荐景点、控制预算、安排交通和美食", "multi"),
    ]

    for q, mode in test_cases:
        print("=" * 60)
        print(f"提问：{q}")
        print(f"运行模式：{mode}")
        print("-" * 60)
        # 入参改为字典，传入问题+模式
        result = run(q, mode)
        print(f"输出结果：\n{result}")
        print("=" * 60 + "\n")

    print("🚀 旅行计划生成器测试")
    plan = asyncio.run(generate_travel_plan("三亚", 5, 8000))
    print(plan)


if __name__ == "__main__":
    main()
