from bases.models import MongoModel
from bases.settings import settings
from bases.utils import now_utc


# 日志
class Log(MongoModel):

    def __init__(self):
        super(Log, self).__init__(settings['mongo']['name'], "Log")

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
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "username": self.username,
                "method": self.method,
                "uri": self.uri,
                "params": self.params,
                "ip": self.ip,
                "times": self.times,
                "add_time": now_utc()}
