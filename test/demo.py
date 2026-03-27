import os
from fastapi import FastAPI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_classic.chains import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# 替换掉原来的 OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
import pymysql

from config.settings import settings

app = FastAPI()

# 2. 初始化本地 Embedding 模型 (完全免费，不走网络)
# 这个模型很小，第一次运行会自动下载，之后就是本地运行了
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. 模拟数据
texts = [
    "寄往美国的液体类物品属于限制运输品，需提供MSDS报告。",
    "智慧物流系统3.0版本支持实时路径规划，响应时间小于200ms。"
]

# 4. 初始化向量数据库 (使用刚刚定义的本地 embeddings)
vectorstore = Chroma.from_texts(
    texts,
    embedding=embeddings,  # 使用本地模型
    persist_directory="./chroma_db"  # 建议持久化到本地，下次不用重新创建
)


@app.get("/chat")
async def chat_with_ai(user_query: str):
    # LLM 还是用 API
    llm = ChatOpenAI(
        model_name=settings.MODEL_NAME,
        openai_api_key=settings.MODEL_API_KEY,
        openai_api_base=settings.MODEL_BASE_URL,  # 加上 v1 试试
        temperature=0
    )

    # 检索
    docs = vectorstore.similarity_search(user_query, k=1)
    context = docs[0].page_content if docs else ""

    prompt = f"已知信息：{context}\n问题：{user_query}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# Agent创建例子1
# from langchain_community.tools import DuckDuckGoSearchRun
#
# # 1. 定义工具
# tools = [
#     DuckDuckGoSearchRun(),  # 搜索工具
#     CalculatorInput()  # 计算工具
# ]
#
# # 2. 自定义 Prompt (让它说话幽默点)
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "你是一个幽默的助手。在回答前先搜索最新信息，如果需要计算请使用计算器。"),
#     ("human", "{input}"),
#     ("placeholder", "{agent_scratchpad}"),
# ])
#
# # 3 & 4. 组装并执行
# agent = create_tool_calling_agent(llm, tools, prompt)
# executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
#
# executor.invoke({"input": "今天特斯拉股价是多少？如果买10股需要多少钱？"})


# Agent创建例子2
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_community.agent_toolkits import SQLDatabaseToolkit # 举例：SQL 工具包
# # 或者引入你自己的自定义工具
# # from my_tools import my_custom_tool
#
# # 1. 准备工具 (Tools)
# # 可以是列表，也可以是 Toolkit (工具包)
# tools = [...]
# # 例如：tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
#
# # 2. 准备提示词 (Prompt)
# # 这是控制智能体行为的核心
# from langchain.prompts import ChatPromptTemplate
#
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "你是一个专业的数据分析师助手。请始终先思考，再行动。"),
#     ("human", "{input}"),
#     # 必须包含 {agent_scratchpad} 占位符，用于存放历史思考过程
#     ("placeholder", "{agent_scratchpad}"),
# ])
#
# # 3. 创建 Agent 逻辑对象 (不是 Executor)
# # 注意：这里不再传入 agent_type 字符串，而是直接绑定 prompt 和 tools
# agent = create_tool_calling_agent(llm, tools, prompt)
#
# # 4. 创建执行器 (Executor)
# # 这里是真正控制循环、最大迭代次数、错误处理的地方
# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True,
#     max_iterations=5,          # 防止死循环
#     max_execution_time=60,     # 防止超时
#     handle_parsing_errors=True # 自动处理解析错误
# )
#
# # 5. 调用
# result = agent_executor.invoke({"input": "你的问题"})