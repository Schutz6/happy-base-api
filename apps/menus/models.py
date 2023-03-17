from bases.models import MongoModel
from bases.settings import settings


# 菜单
class Menu(MongoModel):

    def __init__(self):
        super(Menu, self).__init__(settings['mongo']['name'], "Menu")

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
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "pid": self.pid,
                "name": self.name,
                "icon": self.icon,
                "url": self.url,
                "roles": self.roles,
                "level": self.level,
                "status": self.status,
                "sort": self.sort}
