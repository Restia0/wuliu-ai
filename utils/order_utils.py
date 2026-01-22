import time
import random


def generate_order_no() -> str:
    """
    生成唯一订单号：13位时间戳 + 4位随机数
    示例：1736985600123 + 8888 = 17369856001238888
    :return:
    """
    # 获取当前时间戳
    timestamp = str(int(time.time() * 1000))
    # 生成随机数
    random_num = str(random.randint(1000, 9999))
    # 组装订单编号
    order_number = timestamp + random_num
    return order_number
