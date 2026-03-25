"""OCR工具类：PDF转文本、大模型提取订单信息"""
import json

from alibabacloud_ocr_api20210707.models import RecognizeAllTextRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_ocr_api20210707.client import Client as OcrClient
from alibabacloud_tea_util.models import RuntimeOptions
from openai import OpenAI

from config.settings import settings
from utils.common_utils import logger
from utils.prompt_utils import SystemPrompt


# ======================== 阿里云 OCR 客户端 ========================
def get_aliyun_ocr_client():
    config = Config(
        access_key_id=settings.ALIBABA_CLOUD_ACCESS_KEY_ID,
        access_key_secret=settings.ALIBABA_CLOUD_ACCESS_KEY_SECRET,
        endpoint=f"ocr-api.{settings.ALIBABA_OCR_REGION}.aliyuncs.com",
    )
    return OcrClient(config)


def aliyun_ocr_pdf(pdf_path: str) -> str:
    """
    阿里云OCR直接识别PDF
    """
    try:
        client = get_aliyun_ocr_client()
        # 运行参数connect_timeout和read_timeout参数在Config中也有，区别：Config中是全局的超时时间，而RuntimeOptions是针对单个请求的超时时间。
        runtime = RuntimeOptions(
            connect_timeout=15000,  # 连接超时
            read_timeout=120000,    # 读取超时
            autoretry=True,
        )

        # 读取PDF文件字节
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        # 阿里云OCR直接识别PDF
        request = RecognizeAllTextRequest(
            body=pdf_bytes,
            type="Advanced",
        )

        # 3. 调用接口
        response = client.recognize_all_text_with_options(request, runtime)
        result = response.body.to_map()

        # 4. 提取识别文本
        ocr_text = ""
        if result.get("Data") and result["Data"].get("Content"):
            ocr_text = result["Data"]["Content"]

        logger.info(f"阿里云 OCR 识别成功：{pdf_path}")
        return ocr_text.strip()

    except Exception as e:
        logger.error(f"OCR 识别失败：{str(e)}")
        raise ValueError(f"OCR 识别失败：{str(e)}")


# ======================== 统一入口（不变） ========================
def pdf_to_text(pdf_path: str) -> str:
    return aliyun_ocr_pdf(pdf_path)


# ======================== 大模型提取订单信息（不变） ========================
def extract_order_info_with_llm(ocr_text: str) -> dict:
    client = OpenAI(
        api_key=settings.MODEL_API_KEY,
        base_url=settings.MODEL_BASE_URL,
    )
    prompt = SystemPrompt.ORDER_EXTRACT.value
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"请从以下货物单据中获取信息，输出为结构化的json格式：{ocr_text}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"大模型提取成功：{result}")
        return json.loads(result)
    except Exception as e:
        logger.error(f"大模型提取失败：{e}")
        raise ValueError(f"大模型提取失败：{e}")
