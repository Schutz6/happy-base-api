from bases.models import MongoModel
from bases.settings import settings
from bases.utils import now


# 角色
class Role(MongoModel):

    def __init__(self):
        super(Role, self).__init__(settings['mongo']['name'], "Role")

    """数据库字段说明"""
    # 唯一ID
    name = None
    # 角色
    describe = None
    # 备注
    remarks = None

    # 格式化json
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "name": self.name,
                "describe": self.describe,
                "remarks": self.remarks,
                "add_time": now()}
