from bases.utils import mongo_helper


class Role(object):
    """角色"""

    # 文档名
    collection_name = "Role"

    """数据库字段说明"""
    # 唯一ID
    name = None
    # 角色
    describe = None
    # 备注
    remarks = None
    # 排序
    sort = 0

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Role.collection_name)
        return {"_id": _id,
                "name": req_data.get("name"),
                "describe": req_data.get("describe"),
                "remarks": req_data.get("remarks"),
                "sort": req_data.get("sort", 0)}
