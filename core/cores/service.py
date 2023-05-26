import json

from core.codes.models import Code
from base.keys import Keys
from base.utils import redis_helper, mongo_helper


class CoreService(object):
    """核心服务类"""

    @staticmethod
    def remove_mid(mid):
        """删除模块"""
        redis_helper.redis.delete(Keys.codeKey + mid)

    @staticmethod
    async def get_module(mid):
        """获取模块"""
        module = redis_helper.redis.get(Keys.codeKey + mid)
        if module is None:
            module = await mongo_helper.fetch_one(Code.collection_name, {"mid": mid})
            if module is not None:
                # 存储
                redis_helper.redis.set(Keys.codeKey + mid, json.dumps(module))
        else:
            module = json.loads(module)
        return module

    @staticmethod
    def remove_obj(mid, _id):
        """删除对象缓存"""
        redis_helper.redis.delete(Keys.objectKey + mid + ":" + str(_id))

    @staticmethod
    async def get_obj(mid, _id):
        """获取模块"""
        obj = redis_helper.redis.get(Keys.objectKey + mid + ":" + str(_id))
        if obj is None:
            obj = await mongo_helper.fetch_one(mid, {"_id": int(_id)})
            if obj is not None:
                # 存储
                redis_helper.redis.set(Keys.objectKey + mid + ":" + str(_id), json.dumps(obj))
        else:
            obj = json.loads(obj)
        return obj