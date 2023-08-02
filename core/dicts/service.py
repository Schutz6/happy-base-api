import json

from base.keys import Keys
from base.utils import redis_helper, mongo_helper


class DictService(object):
    """字典服务类"""

    # 根据用户编号获取离线消息
    @staticmethod
    async def get_dict_list(type_name):
        results = []
        # 获取缓存
        dict_values = redis_helper.redis.get(Keys.dictKey + type_name)
        if dict_values is None:
            dict_values = await mongo_helper.fetch_all("DictValue", {"type_name": type_name},
                                                       [("sort", -1), ("_id", -1)])
            for dict_value in dict_values:
                dict_value["id"] = dict_value["_id"]
                results.append(dict_value)
            redis_helper.redis.set(Keys.dictKey + type_name, json.dumps(results))
        else:
            results = json.loads(dict_values)
        return results

    # 删除缓存
    @staticmethod
    def delete_cache(type_name):
        redis_helper.redis.delete(Keys.dictKey + type_name)
