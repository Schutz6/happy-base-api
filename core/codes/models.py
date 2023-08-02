from base.utils import mongo_helper


class Code(object):
    """代码"""

    # 文档名
    collection_name = "Code"

    """数据库字段说明"""
    # 模块ID
    mid = None
    # 模块名称
    name = None
    # 使用缓存
    cache = 0
    # 是否追溯
    retrace = 0
    # 接口集合
    api_json = []
    # 表结构
    """
    {"name": "字段", "type": "类型", "remarks": "备注", "default": "默认值", 
    "key": "绑定对象/字典", "show": "表格显示", "query": "综合查询", "single_query": "单独查询", "sort": "排序字段", "unique": "唯一校验",
    "edit": "是否编辑", "must": "是否必填"}
    """
    table_json = []

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Code.collection_name)
        return {"_id": _id,
                "mid": req_data.get("mid"),
                "name": req_data.get("name"),
                "cache": req_data.get("cache", 0),
                "retrace": req_data.get("retrace", 0),
                "api_json": req_data.get("api_json", []),
                "table_json": req_data.get("table_json", [])}
