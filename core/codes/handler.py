import json
import re

from core.codes.models import Code
from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func, res_fail_func
from base.utils import mongo_helper
from core.cores.service import CoreService


class AddHandler(BaseHandler):
    """
        添加
        post -> /code/add/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        mid = req_data.get("mid")
        # 判断是否存在
        if mid is not None:
            code = await mongo_helper.fetch_one(Code.collection_name, {"mid": mid})
            if code is not None:
                res['code'] = 50000
                res['message'] = '模块ID已存在'
            else:
                await mongo_helper.insert_one(Code.collection_name, await Code.get_json(req_data))
        else:
            res = res_fail_func(None)
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /code/delete/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            code = await mongo_helper.fetch_one(Code.collection_name, {"_id": _id})
            if code is not None:
                # 删除数据
                await mongo_helper.delete_one(Code.collection_name, {"_id": _id})
                # 删除缓存
                await CoreService.remove_mid(code["mid"])
        self.write(res)


class UpdateHandler(BaseHandler):
    """
        修改
        post -> /code/update/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        mid = req_data.get("mid")
        name = req_data.get("name")
        cache = req_data.get("cache", 0)
        retrace = req_data.get("retrace", 0)
        api_json = req_data.get("api_json", [])
        table_json = req_data.get("table_json", [])

        if _id is not None:
            # 修改数据
            await mongo_helper.update_one(Code.collection_name, {"_id": _id},
                                          {"$set": {"name": name, "cache": cache, "retrace": retrace,
                                                    "api_json": api_json,
                                                    "table_json": table_json}})
            # 删除缓存
            await CoreService.remove_mid(mid)
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /code/list/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)
        search_key = req_data.get("searchKey")

        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["$or"] = [{"mid": re.compile(search_key)}, {"name": re.compile(search_key)}]

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Code.collection_name, query_criteria,
                                                       [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Code.collection_name, query_criteria)

        results = []
        for item in page_data.get("list", []):
            item["id"] = item["_id"]
            item.pop("_id")
            results.append(item)

        data = {
            "total": total,
            "size": page_size,
            "current": current_page,
            "results": results
        }

        res['data'] = data
        self.write(res)


class GetModuleHandler(BaseHandler):
    """
        获取模块
        post -> /code/getModule/
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        mid = req_data.get("mid")
        if mid is not None:
            module = await CoreService.get_module(mid)
            res['data'] = module
        self.write(res)
