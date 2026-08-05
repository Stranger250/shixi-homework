import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel

#第一步：环境配置
load_dotenv(find_dotenv())

#第二步：初始化模型
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model=model_name,
    temperature=0.3
)

#第三步：生成自我介绍
def call_llm(name, job ,skills):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的人力资源顾问，擅长帮人写简洁有力的自我介绍"),
        ("human", "请根据以下信息，帮我写一段 50 字以内的自我介绍。姓名：{name}，职位：{job}，技能：{skills}"),
    ])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"name": name, "job": job, "skills": skills})
    print("模型返回的自我介绍:", result)
    assert isinstance(result, str), "模型返回结果不是字符串类型"
    return result


#第四步：生成个人 slogan（使用PromptTemplate）
def call_llm2(name, job):
    template="""
请根据以下信息，生成一句 15 字以内的个人 slogan，要求朗朗上口。
姓名：{name}，
职位：{job}""".strip()
    prompt = PromptTemplate.from_template(template)
    prompt = prompt.format(name=name, job=job)
    response = llm.invoke(prompt)
    print(f"模型回复的个人 slogan：{response.content}")
    return response.content


#第五步：生成结构化名片数据（使用 JsonOutputParser）
def cll_llm3(name, job, skills):
    class Card(BaseModel):
        name: str
        job: str
        skills: str
        slogan: str

    json_parser = JsonOutputParser(pydantic_object=Card)
    format_rules = json_parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是专业电子名片生成师，严格按照下面JSON格式输出，不要输出任何多余解释、开场白：
        {format_rules}"""),
        ("human", """根据下面信息生成完整名片：
        姓名：{name}
        职位：{job}
        技能：{skills}
        自我介绍控制50字内，slogan控制15字内""")
    ])

    chain = prompt | llm | json_parser
    card_result = chain.invoke({
        "name": name,
        "job": job,
        "skills": skills,
        "format_rules": format_rules
    })
    print("解析后的字典结果:", card_result)
    return card_result


if __name__ == "__main__":
    print("-----------------运行结果----------------")
    intro = call_llm("张三", "开发工程师", "Python, LangChain, FastAPI")
    slogan = call_llm2("张三", "开发工程师")
    card = cll_llm3("张三", "开发工程师", "Python, LangChain, FastAPI")
    
    print("\n============================")
    print("        AI 智能名片")
    print("============================")
    print(f"姓名：{card['name']}")
    print(f"职位：{card['job']}")
    print(f"自我介绍：{intro}")
    print(f"个人 slogan：{slogan}")
    print(f"技能：{card['skills']}")
    print("============================")
