import json

from apps.dicts.models import DictType, DictValue
from apps.dicts.service import DictService
from bases.handler import BaseHandler
from bases.decorators import log_async, authenticated_async
from bases.res import res_func
from bases.config import settings
from bases.utils import mongo_helper


class ListDictTypeHandler(BaseHandler):
    """
        获取字典类型列表
        get -> /dict/typeList/
    """

    @authenticated_async(['admin', 'super'])
    async def get(self):
        res = res_func([])
        # 查询所有
        dict_types = await mongo_helper.fetch_all(DictType.collection_name, {"_id": {"$ne": "sequence_id"}},
                                                  [("_id", -1)])
        results = []
        for dict_type in dict_types:
            dict_type["id"] = dict_type["_id"]
            # 查询子集
            dict_type["children"] = await DictService.get_dict_list(dict_type["_id"])
            results.append(dict_type)
        res['data'] = results
        self.write(res)


class AddDictTypeHandler(BaseHandler):
    """
        新增字典类型
        post -> /dict/typeAdd/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _id = req_data.get("id")
        name = req_data.get("name")
        describe = req_data.get("describe")

        if _id is not None:
            # 编辑
            await mongo_helper.update_one(DictType.collection_name, {"_id": _id},
                                          {"$set": {"name": name, "describe": describe}})
        else:
            # 新增
            await mongo_helper.insert_one(DictType.collection_name, await DictType.get_json(req_data))
        res['message'] = '保存成功'
        self.write(res)


class DeleteDictTypeHandler(BaseHandler):
    """
        删除字典类型
        post -> /dict/typeDelete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            # 删除类型
            await mongo_helper.delete_one(DictType.collection_name, {"_id": _id})

            # 删除值
            await mongo_helper.delete_many(DictValue.collection_name, {"dict_tid": _id})

            # 删除缓存
            DictService.delete_cache(_id)

        res['message'] = '删除成功'
        self.write(res)


class ListDictValueHandler(BaseHandler):
    """
        获取字典值列表
        post -> /dict/valueList/
    """

    @log_async
    async def post(self):
        res = res_func([])
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        dict_tid = req_data.get("dict_tid")

        if dict_tid is not None:
            res['data'] = await DictService.get_dict_list(dict_tid)
        self.write(res)


class AddDictValueHandler(BaseHandler):
    """
        新增字典值
        post -> /dict/valueAdd/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _id = req_data.get("id")
        dict_name = req_data.get("dict_name")
        dict_value = req_data.get("dict_value")
        sort = req_data.get("sort", 0)
        dict_tid = req_data.get("dict_tid", 0)

        if _id is not None:
            # 编辑
            await mongo_helper.update_one(DictValue.collection_name, {"_id": _id},
                                          {"$set": {"dict_name": dict_name, "dict_value": dict_value, "sort": sort}})
        else:
            # 新增
            await mongo_helper.insert_one(DictValue.collection_name, await DictValue.get_json(req_data))
            res['message'] = '添加成功'
        # 删除缓存
        DictService.delete_cache(dict_tid)
        self.write(res)


class DeleteDictValueHandler(BaseHandler):
    """
        删除字典值
        post -> /dict/valueDelete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _id = req_data.get("id")
        dict_tid = req_data.get("dict_tid")

        if _id is not None:
            await mongo_helper.delete_one(DictValue.collection_name, {"_id": _id})
            # 删除缓存
            DictService.delete_cache(dict_tid)
        self.write(res)


class GetDictListHandler(BaseHandler):
    """
        获取字典列表
        post -> /dict/getList/
    """

    @log_async
    async def post(self):
        res = res_func([])
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        name = req_data.get("name")

        dict_type = await mongo_helper.fetch_one(DictType.collection_name, {"name": name})
        if dict_type is not None:
            results = []
            query = await DictService.get_dict_list(dict_type["_id"])
            if name == "Avatar":
                # 头像处理
                for item in query:
                    item["dict_value"] = settings['SITE_URL'] + item["dict_value"]
                    results.append({"text": item["dict_name"], "value": item["dict_value"]})
            else:
                for item in query:
                    results.append({"text": item["dict_name"], "value": item["dict_value"]})
            res['data'] = results
        self.write(res)
