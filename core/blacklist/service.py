from datetime import datetime

from core.blacklist.models import Blacklist
from base.keys import Keys
from base.utils import redis_helper, mongo_helper, now_utc


class BlacklistService(object):
    """黑名单服务类"""

    # 添加到黑名单
    @staticmethod
    async def add_ip_blacklist(ip):
        # 加入到缓存
        redis_helper.redis.set(Keys.ipBlacklistKey + ip, 1)
        # 入库
        await mongo_helper.insert_one(Blacklist.collection_name, {"ip": ip, "add_time": now_utc()})

    # 删除黑名单
    @staticmethod
    async def remove_ip_blacklist(ip):
        # 删除缓存
        redis_helper.redis.delete(Keys.ipBlacklistKey+ip)
        # 删除数据库
        await mongo_helper.delete_one(Blacklist.collection_name, {"ip": ip})

    # 判断IP是否在黑名单
    @staticmethod
    async def has_ip_blacklist(ip):
        blacklist = redis_helper.redis.get(Keys.ipBlacklistKey + ip)
        if blacklist is None:
            return False
        else:
            return True

    # 获取IP访问次数
    @staticmethod
    def get_ip_limit(ip):
        s = datetime.now().strftime("%S")
        key = Keys.ipLimitKey + s + ":" + ip
        num = redis_helper.redis.get(key)
        if num is None:
            # 初始化
            num = 1
            redis_helper.redis.set(key, num, ex=1)
        else:
            # 增加一次
            num = int(num) + 1
            redis_helper.redis.incr(key)
        return num

    # 获取总接口访问次数
    @staticmethod
    def get_api_limit():
        s = datetime.now().strftime("%S")
        key = Keys.apiLimitKey + ":" + s
        num = redis_helper.redis.get(key)
        if num is None:
            # 初始化
            num = 1
            redis_helper.redis.set(key, num, ex=1)
        else:
            # 增加一次
            num = int(num) + 1
            redis_helper.redis.incr(key)
        return num
