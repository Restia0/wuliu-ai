"""日志中间件：记录请求/响应全链路日志"""
import time
import json
from fastapi import Request
from starlette.responses import JSONResponse
from utils.common_utils import logger  # 复用现有日志实例

# class LogMiddleware(BaseHTTPMiddleware):
#     """
#     日志中间件
#     功能：
#     1. 记录请求的路径、方法、参数、用户ID/角色
#     2. 记录响应的状态码、耗时
#     3. 异常请求单独标记，ERROR级别输出
#     4. 可配置忽略的路径（如/health）
#     """
#
#     def __init__(self, app, ignore_paths: list = None):
#         super().__init__(app)
#         # 忽略的路径（不记录日志）
#         self.ignore_paths = ignore_paths or ["/health", "/api/v1/ping", "/docs", "/redoc"]
#
#     async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
#         # 1. 过滤忽略的路径
#         if request.url.path in self.ignore_paths:
#             return await call_next(request)
#
#         # 2. 记录请求开始时间
#         start_time = time.time()
#
#         # 3. 提取请求基础信息
#         request_info = {
#             "method": request.method,
#             "path": request.url.path,
#             "query_params": dict(request.query_params),
#             "client_ip": request.client.host if request.client else "unknown",
#             "user_agent": request.headers.get("user-agent", "unknown")
#         }
#
#         # 4. 提取用户信息（从request.state，需和认证中间件配合）
#         try:
#             request_info["user_id"] = request.state.user_id if hasattr(request.state, "user_id") else "anonymous"
#             request_info["user_role"] = request.state.role if hasattr(request.state, "role") else "anonymous"
#         except Exception:
#             request_info["user_id"] = "anonymous"
#             request_info["user_role"] = "anonymous"
#
#         # 5. 提取请求体（仅POST/PUT等方法）
#         try:
#             if request.method in ["POST", "PUT", "PATCH"] and request.headers.get("content-type") == "application/json":
#                 request_body = await request.json()
#                 # 脱敏处理：隐藏手机号、密码等敏感信息
#                 if "phone" in request_body:
#                     request_body["phone"] = self._desensitize_str(request_body["phone"])
#                 if "password" in request_body:
#                     request_body["password"] = "******"
#                 request_info["body"] = request_body
#             else:
#                 request_info["body"] = None
#         except Exception as e:
#             request_info["body"] = f"解析请求体失败：{str(e)}"
#
#         # 6. 处理请求并记录响应
#         try:
#             response = await call_next(request)
#
#             # 7. 计算耗时（毫秒）
#             process_time = round((time.time() - start_time) * 1000, 2)
#
#             # 8. 提取响应信息
#             response_info = {
#                 "status_code": response.status_code,
#                 "process_time_ms": process_time
#             }
#
#             # 9. 记录正常请求日志（INFO级别）
#             log_msg = (
#                 f"REQUEST - {json.dumps(request_info, ensure_ascii=False)} | "
#                 f"RESPONSE - {json.dumps(response_info, ensure_ascii=False)}"
#             )
#             logger.info(log_msg)
#
#             return response
#
#         # 10. 处理异常请求
#         except Exception as e:
#             # 计算耗时
#             process_time = round((time.time() - start_time) * 1000, 2)
#
#             # 记录异常日志（ERROR级别）
#             error_info = {
#                 "status_code": 500,
#                 "process_time_ms": process_time,
#                 "error": str(e)
#             }
#
#             log_msg = (
#                 f"REQUEST - {json.dumps(request_info, ensure_ascii=False)} | "
#                 f"ERROR - {json.dumps(error_info, ensure_ascii=False)}"
#             )
#             logger.error(log_msg)
#
#             # 返回统一异常响应
#             return JSONResponse(
#                 status_code=500,
#                 content={"code": 500, "message": "服务器内部错误", "data": None}
#             )
#
#     @staticmethod
#     def _desensitize_str(s: str) -> str:
#         """字符串脱敏（手机号：138****1234，姓名：张**）"""
#         if not s:
#             return s
#         # 手机号脱敏
#         if len(s) == 11 and s.isdigit():
#             return f"{s[:3]}****{s[-4:]}"
#         # 姓名脱敏（2字：张*，3字：张**）
#         elif len(s) <= 3 and not s.isdigit():
#             return f"{s[0]}{'*' * (len(s) - 1)}"
#         # 其他字符串（保留前3后2，中间*）
#         else:
#             return f"{s[:3]}****{s[-2:]}" if len(s) > 5 else f"{s[:1]}****"


# 忽略的路径常量
IGNORE_PATHS = ["/health", "/api/v1/ping", "/docs", "/redoc"]


async def log_middleware(request: Request, call_next):
    """
    日志中间件（函数形式）
    功能：
    1. 记录请求的路径、方法、参数、用户 ID/角色
    2. 记录响应的状态码、耗时
    3. 异常请求单独标记，ERROR 级别输出
    4. 可配置忽略的路径（如/health）
    """
    # 1. 过滤忽略的路径
    if request.url.path in IGNORE_PATHS:
        return await call_next(request)

    # 2. 记录请求开始时间
    start_time = time.time()

    # 3. 提取请求基础信息
    request_info = {
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    }

    # 4. 提取用户信息（从 request.state，需和认证中间件配合）
    try:
        request_info["user_id"] = request.state.user_id if hasattr(request.state, "user_id") else "anonymous"
        request_info["user_role"] = request.state.role if hasattr(request.state, "role") else "anonymous"
    except Exception:
        request_info["user_id"] = "anonymous"
        request_info["user_role"] = "anonymous"

    # 5. 提取请求体（仅 POST/PUT等方法）
    try:
        if request.method in ["POST", "PUT", "PATCH"] and request.headers.get("content-type") == "application/json":
            request_body = await request.json()
            # 脱敏处理：隐藏手机号、密码等敏感信息
            if "phone" in request_body:
                request_body["phone"] = _desensitize_str(request_body["phone"])
            if "password" in request_body:
                request_body["password"] = "******"
            request_info["body"] = request_body
        else:
            request_info["body"] = None
    except Exception as e:
        request_info["body"] = f"解析请求体失败：{str(e)}"

    # 6. 处理请求并记录响应
    try:
        response = await call_next(request)

        # 7. 计算耗时（毫秒）
        process_time = round((time.time() - start_time) * 1000, 2)

        # 8. 提取响应信息
        response_info = {
            "status_code": response.status_code,
            "process_time_ms": process_time
        }

        # 9. 记录正常请求日志（INFO 级别）
        log_msg = (
            f"REQUEST - {json.dumps(request_info, ensure_ascii=False)} | "
            f"RESPONSE - {json.dumps(response_info, ensure_ascii=False)}"
        )
        logger.info(log_msg)

        return response

    # 10. 处理异常请求
    except Exception as e:
        # 计算耗时
        process_time = round((time.time() - start_time) * 1000, 2)

        # 记录异常日志（ERROR 级别）
        error_info = {
            "status_code": 500,
            "process_time_ms": process_time,
            "error": str(e)
        }

        log_msg = (
            f"REQUEST - {json.dumps(request_info, ensure_ascii=False)} | "
            f"ERROR - {json.dumps(error_info, ensure_ascii=False)}"
        )
        logger.error(log_msg)

        # 返回统一异常响应
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误", "data": None}
        )


def _desensitize_str(s: str) -> str:
    """字符串脱敏（手机号：138****1234，姓名：张**）"""
    if not s:
        return s
    # 手机号脱敏
    if len(s) == 11 and s.isdigit():
        return f"{s[:3]}****{s[-4:]}"
    # 姓名脱敏（2 字：张*，3 字：张**）
    elif len(s) <= 3 and not s.isdigit():
        return f"{s[0]}{'*' * (len(s) - 1)}"
    # 其他字符串（保留前 3 后 2，中间*）
    else:
        return f"{s[:3]}****{s[-2:]}" if len(s) > 5 else f"{s[:1]}****"