import os
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
# 替换掉原来的 OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
import pymysql

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
        model_name="deepseek-chat",
        openai_api_key="sk-bb54ee822ff349889028e1d901bb626d",
        openai_api_base="https://api.deepseek.com/v1",  # 加上 v1 试试
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