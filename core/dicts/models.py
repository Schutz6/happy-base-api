from base.utils import mongo_helper


class DictType(object):
    """字典类型"""

    # 文档名
    collection_name = "DictType"

    """数据库字段说明"""
    # 类型名称
    name = None
    # 类型描述
    describe = None

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(DictType.collection_name)
        return {"_id": _id,
                "name": req_data.get("name"),
                "describe": req_data.get("describe")}


class DictValue(object):
    """字典值"""

    # 文档名
    collection_name = "DictValue"

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
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(DictValue.collection_name)
        return {"_id": _id,
                "dict_tid": req_data.get("dict_tid", 0),
                "dict_name": req_data.get("dict_name"),
                "dict_value": req_data.get("dict_value"),
                "sort": req_data.get("sort", 0)}

