import json
import re

from apps.params.models import Param
from bases.decorators import authenticated_async, log_async
from bases.handler import BaseHandler
from bases.res import res_func
from bases.utils import mongo_helper


class AddHandler(BaseHandler):
    """
        添加
        post -> /param/add/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        key = req_data.get("key")

        # 查找是否存在
        param = await mongo_helper.fetch_one(Param.collection_name, {"key": key})
        if param is not None:
            res['code'] = 50000
            res['message'] = '该唯一ID已存在'
        else:
            await mongo_helper.insert_one(Param.collection_name, await Param.get_json(req_data))
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /param/delete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        
        if _id is not None:
            # 删除数据
            await mongo_helper.delete_one(Param.collection_name, {"_id": _id})
        self.write(res)


class UpdateHandler(BaseHandler):
    """
        修改
        post -> /param/update/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        value = req_data.get("value")
        remarks = req_data.get("remarks")
        status = req_data.get("status")
        
        if _id is not None:
            # 修改数据
            await mongo_helper.update_one(Param.collection_name, {"_id": _id},
                                          {"$set": {"value": value, "remarks": remarks, "status": status}})
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /param/list/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)
        search_key = req_data.get("searchKey")
        status = req_data.get("status")

        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["$or"] = [{"key": re.compile(search_key)}, {"value": re.compile(search_key)},
                                     {"remarks": re.compile(search_key)}]
        if status is not None:
            query_criteria["status"] = status
        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Param.collection_name, query_criteria, [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Param.collection_name, query_criteria)

        results = []
        for item in page_data.get("list", []):
            item["id"] = item["_id"]
            results.append(item)

        data = {
            "total": total,
            "size": page_size,
            "current": current_page,
            "results": results
        }

        res['data'] = data
        self.write(res)


class GetListHandler(BaseHandler):
    """
        所有列表
        get -> /param/getList/
    """

    @log_async
    async def get(self):
        res = res_func({})
        query = await mongo_helper.fetch_all(Param.collection_name, {"status": 0}, [("_id", -1)])
        results = []
        for item in query:
            results.append((item["key"], item["value"]))
        # 转成字典格式
        res['data'] = dict(results)
        self.write(res)
