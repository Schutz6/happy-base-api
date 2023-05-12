from bases.utils import mongo_helper


class Param(object):
    """系统参数"""

    # 文档名
    collection_name = "Param"

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
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Param.collection_name)
        return {"_id": _id,
                "key": req_data.get("key"),
                "value": req_data.get("value"),
                "status": req_data.get("status"),
                "remarks": req_data.get("remarks")}
