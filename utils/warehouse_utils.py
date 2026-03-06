from dao.warehouse_dao import warehouse_dao


def get_warehouse_area_map() -> dict:
    """
    从数据库读取仓库-区域映射字典：{省/市: 仓库ID}
    优先级：市 > 省（如广州市有仓库则优先匹配，无则匹配广东省仓库）
    :return:
    """
    # 获取所有有效仓库
    warehouses = warehouse_dao.get_all_valid_warehouses()
    area_map = {}

    for warehouse in warehouses:
        # 市级别映射
        if warehouse.get("city"):
            area_map[warehouse["city"]] = warehouse["id"]
        # 省级别映射，仅当该省无市级别映射时添加
        if warehouse.get("province") and warehouse["province"] not in area_map:
            area_map[warehouse["province"]] = warehouse["id"]

    return area_map


def match_warehouse_by_address(province: str, city: str) -> int:
    """
    根据省/市匹配仓库ID
    :param province:发件省
    :param city:发件市
    :return:匹配到的仓库ID，无匹配则返回默认仓库ID
    """
    area_map = get_warehouse_area_map()
    # 优先匹配市
    if city in area_map:
        return area_map[city]
    # 再匹配省
    if province in area_map:
        return area_map[province]
    # 无匹配则返回默认仓库ID
    default_warehouse = warehouse_dao.get_default_warehouse()
    return default_warehouse["id"] if default_warehouse else 1
