import json

from core.codes.models import Code
from base.keys import Keys
from base.utils import redis_helper, mongo_helper


class CoreService(object):
    """核心服务类"""

    @staticmethod
    async def remove_mid(mid):
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
    async def remove_obj(mid, _id):
        """删除对象缓存"""
        redis_helper.redis.delete(Keys.objectKey + mid + ":" + str(_id))
        keys = redis_helper.redis.keys(pattern=Keys.categoryKey + mid + ":*")
        for key in keys:
            redis_helper.redis.delete(key)

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

    @staticmethod
    async def remove_category(mid):
        """删除分类缓存"""
        keys = redis_helper.redis.keys(pattern=Keys.categoryKey + mid + ":*")
        for key in keys:
            redis_helper.redis.delete(key)

    @staticmethod
    async def get_category(mid, type_id):
        """获取分类列表"""
        category = redis_helper.redis.get(Keys.categoryKey + mid + ":" + str(type_id))
        if category is None:
            results = []
            # 查询一级分类
            if type_id > 0:
                query_one = await mongo_helper.fetch_all(mid, {"pid": 0, "type_id": type_id}, [("sort", -1), ("_id", -1)])
            else:
                query_one = await mongo_helper.fetch_all(mid, {"pid": 0}, [("sort", -1), ("_id", -1)])
            for one in query_one:
                one["id"] = one["_id"]
                one.pop("_id")
                results.append(one)
                # 查询二级分类
                if type_id > 0:
                    query_two = await mongo_helper.fetch_all(mid, {"pid": one["id"], "type_id": type_id},  [("sort", -1), ("_id", -1)])
                else:
                    query_two = await mongo_helper.fetch_all(mid, {"pid": one["id"]}, [("sort", -1), ("_id", -1)])
                for two in query_two:
                    two["id"] = two["_id"]
                    two.pop("_id")
                    results.append(two)
                    # 查询三级分类
                    if type_id > 0:
                        query_three = await mongo_helper.fetch_all(mid, {"pid": two["id"], "type_id": type_id}, [("sort", -1), ("_id", -1)])
                    else:
                        query_three = await mongo_helper.fetch_all(mid, {"pid": two["id"]}, [("sort", -1), ("_id", -1)])
                    for three in query_three:
                        three["id"] = three["_id"]
                        three.pop("_id")
                        results.append(three)
            # 存储
            if len(results) > 0:
                redis_helper.redis.set(Keys.categoryKey + mid + ":" + str(type_id), json.dumps(results))
        else:
            results = json.loads(category)
        return results
