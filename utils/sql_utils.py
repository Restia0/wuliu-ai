import re

from langchain_classic.agents import AgentExecutor, AgentType
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from overrides import overrides
from sqlalchemy import create_engine, Executable

from config.settings import settings
from utils.common_utils import logger
from utils.prompt_utils import SystemPrompt

DANGER_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "TRUNCATE", "CREATE", "GRANT", "LOCK", "UNION", "INTO"
]


def is_safe_select(sql: str) -> bool:
    """
    严格安全检查：
    1. 必须以 SELECT 开头
    2. 不允许任何危险关键字
    3. 仅允许查询
    """
    if not sql:
        return False
    sql_upper = sql.strip().upper()
    # 必须是 SELECT 开头
    if not sql_upper.startswith("SELECT"):
        logger.warning(f"[安全拦截] 非SELECT语句：{sql}")
        return False

    # 使用正则表达式匹配完整的单词（避免误判 is_delete 这样的字段名）
    for keyword in DANGER_KEYWORDS:
        # \b 表示单词边界，确保匹配的是完整单词而非子串
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            logger.warning(f"[安全拦截] 存在危险关键词：{keyword}")
            return False

    return True


# 自定义安全SQL执行器
class SafeSQLDatabase(SQLDatabase):
    @overrides
    def run(
            self,
            command: str | Executable,
            *args,
            parameters: dict | None = None,
            **kwargs
    ) -> str:
        # 转字符串校验
        sql_str = str(command)
        # 【关键防护】
        if not is_safe_select(sql_str):
            raise ValueError("[安全拦截] 非SELECT语句")
        return super().run(command, *args, parameters=parameters, **kwargs)


def get_sql_db() -> SafeSQLDatabase:
    db_uri = settings.MYSQL_URL
    engine = create_engine(db_uri)

    # 使用【安全版】SQLDatabase
    db = SafeSQLDatabase(
        engine,
        include_tables=["core_user", "core_driver_ext", "core_warehouse", "core_order", "core_inbound",
                        "core_outbound"],
        sample_rows_in_table_info=0,
        view_support=True
    )
    return db


# 创建sql智能体
def get_sql_agent_executor() -> AgentExecutor:
    llm = ChatOpenAI(
        model_name=settings.MODEL_NAME,
        openai_api_key=settings.MODEL_API_KEY,
        openai_api_base=settings.MODEL_BASE_URL,
        temperature=0.1
    )
    db = get_sql_db()
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        prefix=SystemPrompt.SQL_PREFIX.value,
        format_instructions=SystemPrompt.SQL_FORMAT_INSTRUCTIONS.value,
        suffix=SystemPrompt.SQL_SUFFIX.value,
        agent_executor_kwargs={
            "return_intermediate_steps": True,  # 返回中间步骤
            "handle_parsing_errors": True,  # 自动处理解析错误
        }
    )
    return agent


def agent_text_to_sql(question: str):
    try:
        agent = get_sql_agent_executor()
        result = agent.invoke({"input": question}, return_only_outputs=False)

        # 从 intermediate_steps 中提取 SQL 和查询结果
        steps = result.get("intermediate_steps", [])

        sql = None
        query_result = None

        if steps:
            # 直接获取最后一步元组
            last_step = steps[-1]
            # 获取AgentAction对象，AgentAction对象有三个熟悉：tool存使用的工具，tool_input存传递给工具的参数（这里是sql），log存中间步骤的日志
            tool_action = last_step[0]
            # 获取查询结果
            tool_result = last_step[1]
            # 从AgentAction对象中取出tool_input属性
            sql = tool_action.tool_input
            # 获取查询结果
            query_result = tool_result

        return {
            "question": question,
            "generated_sql": sql,
            "query_result": query_result,
            "answer": result.get("output", ""),
        }
    except Exception as e:
        logger.error(f"Agent执行错误：{str(e)}")
        raise ValueError(f"智能查询失败：{str(e)}")
