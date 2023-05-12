from bases.utils import now_utc, mongo_helper


class Log(object):
    """系统日志"""

    # 文档名
    collection_name = "Log"

    """数据库字段说明"""
    # 账号
    username = None
    # 接口类型
    method = None
    # 接口
    uri = None
    # 参数
    params = None
    # ip
    ip = None
    # 请求时间
    times = None

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Log.collection_name)
        return {"_id": _id,
                "username": req_data.get("username"),
                "method": req_data.get("method"),
                "uri": req_data.get("uri"),
                "params": req_data.get("params"),
                "ip": req_data.get("ip"),
                "times": req_data.get("times"),
                "add_time": now_utc()}
