from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_classic.agents import create_react_agent, AgentExecutor, create_tool_calling_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import settings
from dao.order_dao import order_dao
from utils.common_utils import logger
from utils.prompt_utils import SystemPrompt


# 本地embedding模型方案
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=settings.HF_MODEL_NAME,
        cache_folder=settings.HF_DOWNLOAD_DISK,
        model_kwargs={
            "device": "cpu",
            "local_files_only": True}
    )


# 创建Chroma向量数据库
def get_vector_store():
    return Chroma(
        collection_name="logistics_faq",
        embedding_function=get_embeddings(),
        persist_directory=settings.CHROMA_DATABASE_PATH
    )


# Chunk切片策略
def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=300,  # 每个切片大小
        chunk_overlap=50,  # 切片内容重叠部分
        separators=["\n\n", "\n", "。", " "]
    )


# PDF 上传 → 切片 → 入库
def upload_pdf_to_vector_db(pdf_path: str):
    try:
        # 1. 加载 PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # 2. 分割文本
        splitter = get_text_splitter()
        chunks = splitter.split_documents(documents)

        # 3. 添加到向量数据库（自动持久化）
        db = get_vector_store()
        db.add_documents(chunks)

        logger.info(f"成功导入 {len(chunks)} 个文档块到向量数据库")
        return len(chunks)
    except Exception as e:
        logger.error(f"导入 PDF 失败：{str(e)}")
        raise


# RAG检索
def rag_retrieve(question: str):
    db = get_vector_store()
    retrieve = db.as_retriever(search_kwargs={"k": 3})
    docs = retrieve.invoke(question)
    if not docs:
        logger.warning(f"未检索到与 '{question}' 相关的知识")
        return "", []
    context = "\n".join([d.page_content for d in docs])
    return context


# RAG工具
@tool
def search_logistics_knowledge(question: str) -> str:
    """
    搜索物流知识库来获取与问题相关的信息。
    当用户询问运费、配送时间、仓储规则等物流相关问题时使用此工具。
    Args:
        question: 用户的自然语言问题
    Returns:
        检索到的相关知识内容
    """
    content = rag_retrieve(question)
    return content if content else "未找到相关信息"


@tool
def query_order_by_no(order_no: str) -> dict:
    """
    通过订单号查询订单详细信息。订单号（时间戳+随即数组成）示例：17369856001238881的形式
    当用户希望通过订单号查询订单信息时调用该工具。
    Args:
        order_no: 订单号
    Returns:
        订单的详细信息（JSON 格式）
    """
    order = order_dao.get_order_by_no(order_no)
    return order if order else "未找到该订单"


def get_rag_agent():
    # llm大模型
    llm = ChatOpenAI(
        model_name=settings.MODEL_NAME,
        openai_api_key=settings.MODEL_API_KEY,
        openai_api_base=settings.MODEL_BASE_URL,
        temperature=1.0
    )

    tools = [
        search_logistics_knowledge,
        query_order_by_no
    ]

    # react形式的提示词与智能体
    # prompt = PromptTemplate.from_template(SystemPrompt.FAQ_REACT_PROMPT.value)
    # agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    # tool-calling形式提示词与智能体
    prompt = ChatPromptTemplate.from_messages([
        ("system", SystemPrompt.FAQ_TOOL_CALLING_PROMPT.value),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor


# 启动agent服务
def rag_agent_run(question: str):
    agent = get_rag_agent()
    result = agent.invoke({"input": question})
    return result.get("output", "")
