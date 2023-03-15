import json

from apps.dicts.models import DictValue
from bases import utils
from bases.service import BaseService


# 字典服务类
class DictService(BaseService):

    # 根据用户编号获取离线消息
    @staticmethod
    async def get_dict_list(dict_tid):
        results = []
        # 获取缓存
        dictValues = DictService.redis.get(DictService.dictKey + str(dict_tid))
        if dictValues is None:
            dictValue_db = DictValue()
            query = await dictValue_db.find_all({"dict_tid": dict_tid})
            dictValues = dictValue_db.query_sort(query, [("sort", 1), ("_id", -1)])
            for dictValue in dictValues:
                dictValue["id"] = dictValue["_id"]
                results.append(dictValue)
            DictService.redis.set(DictService.dictKey + str(dict_tid), json.dumps(results, default=utils.json_serial))
        else:
            results = json.loads(dictValues)
        return results

    # 删除缓存
    @staticmethod
    def delete_cache(dict_tid):
        DictService.redis.delete(DictService.dictKey + str(dict_tid))
