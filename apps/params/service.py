import json

from apps.params.models import Param
from bases.keys import Keys
from bases.utils import redis_helper, mongo_helper


class ParamService(object):

    @staticmethod
    async def get_param(key):
        param = redis_helper.redis.get(Keys.paramsKey + key)
        if param is None:
            param = await mongo_helper.fetch_one(Param.collection_name, {"key": key})
            if param is not None:
                # 存储
                redis_helper.redis.set(Keys.paramsKey + key, json.dumps(param))
        else:
            param = json.loads(param)
        return param

    @staticmethod
    def remove_params(key):
        """删除参数缓存"""
        # 删除全部
        redis_helper.redis.delete(Keys.paramsKey + "0")
        if key is not None:
            # 删除单个
            redis_helper.redis.delete(Keys.paramsKey + key)

    @staticmethod
    async def get_params() -> list:
        """获取参数列表"""
        results = []
        params = redis_helper.redis.get(Keys.paramsKey + "0")
        if params is None:
            query = await mongo_helper.fetch_all(Param.collection_name, {"status": 0}, [("_id", -1)])
            for item in query:
                results.append((item["key"], item["value"]))
            if len(results) > 0:
                # 存储
                redis_helper.redis.set(Keys.paramsKey + "0", json.dumps(results))
        else:
            results = json.loads(params)
        return results
