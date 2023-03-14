from bases.models import MongoModel
from bases.settings import settings
from bases.utils import now


# 字典类型表
class DictType(MongoModel):

    def __init__(self):
        super(DictType, self).__init__(settings['mongo']['name'], "DictType")

    """数据库字段说明"""
    # 类型名称
    name = None
    # 类型描述
    describe = None

    # 格式化json
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "name": self.name,
                "describe": self.describe,
                "add_time": now()}


# 字典值列表
class DictValue(MongoModel):

    def __init__(self):
        super(DictValue, self).__init__(settings['mongo']['name'], "DictValue")

    """数据库字段说明"""
    # 字典类型编号
    dict_tid = None
    # 字典名称
    dict_name = None
    # 字典值
    dict_value = None
    # 自定义排序
    sort = 0

    # 格式化json
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "dict_tid": self.dict_tid,
                "dict_name": self.dict_name,
                "dict_value": self.dict_value,
                "sort": self.sort,
                "add_time": now()}

