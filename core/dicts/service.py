import json

from core.dicts.models import DictValue
from base.keys import Keys
from base.utils import redis_helper, mongo_helper


class DictService(object):
    """字典服务类"""

    # 根据用户编号获取离线消息
    @staticmethod
    async def get_dict_list(dict_tid):
        results = []
        # 获取缓存
        dict_values = redis_helper.redis.get(Keys.dictKey + str(dict_tid))
        if dict_values is None:
            dict_values = await mongo_helper.fetch_all(DictValue.collection_name, {"dict_tid": dict_tid}, [("sort", -1), ("_id", -1)])
            for dict_value in dict_values:
                dict_value["id"] = dict_value["_id"]
                results.append(dict_value)
            redis_helper.redis.set(Keys.dictKey + str(dict_tid), json.dumps(results))
        else:
            results = json.loads(dict_values)
        return results

    # 删除缓存
    @staticmethod
    def delete_cache(dict_tid):
        redis_helper.redis.delete(Keys.dictKey + str(dict_tid))
