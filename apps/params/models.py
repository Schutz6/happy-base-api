from bases.models import MongoModel
from bases.settings import settings


# 参数设置
class Param(MongoModel):

    def __init__(self):
        super(Param, self).__init__(settings['mongo']['name'], "Param")

    """数据库字段说明"""
    # 唯一ID
    key = None
    # 参数值
    value = None
    # 状态 0公共 1隐私
    status = 0
    # 备注
    remarks = None

    # 格式化json
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "key": self.key,
                "value": self.value,
                "status": self.status,
                "remarks": self.remarks}
