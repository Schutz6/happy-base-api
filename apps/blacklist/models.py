from bases.utils import now_utc


class Blacklist(object):
    """IP黑名单"""

    # 文档名
    collection_name = "Blacklist"

    """数据库字段说明"""
    # ip
    ip = None

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        return {"ip": req_data.get("ip"),
                "add_time": now_utc()}
