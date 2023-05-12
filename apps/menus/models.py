from bases.utils import mongo_helper


class Menu(object):
    """菜单"""

    # 文档名
    collection_name = "Menu"

    """数据库字段说明"""
    # 父ID
    pid = 0
    # 名称
    name = None
    # 图标
    icon = None
    # 地址
    url = None
    # 角色
    roles = []
    # 层级
    level = 0
    # 排序
    sort = 0
    # 状态 0禁用 1启用
    status = 0

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Menu.collection_name)
        return {"_id": _id,
                "pid": req_data.get("pid", 0),
                "name": req_data.get("name"),
                "icon": req_data.get("icon"),
                "url": req_data.get("url"),
                "roles": req_data.get("roles", []),
                "level": req_data.get("level", 0),
                "status": req_data.get("status", 0),
                "sort": req_data.get("sort", 0)}
