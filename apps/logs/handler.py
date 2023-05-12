import json
import re

from apps.logs.models import Log
from bases.decorators import authenticated_async
from bases.handler import BaseHandler
from bases.res import res_func
from bases.utils import mongo_helper


class ClearHandler(BaseHandler):
    """
        清空日志
        get -> /log/clear/
    """

    @authenticated_async(['admin', 'super'])
    async def get(self):
        res = res_func({})
        # 清空日志
        await mongo_helper.delete_many(Log.collection_name, {})
        self.write(res)


class BatchDeleteHandler(BaseHandler):
    """
        批量删除
        post -> /log/batchDelete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        ids = req_data.get("ids")

        if ids is not None:
            # 批量删除
            await mongo_helper.delete_many(Log.collection_name, {"_id": {"$in": [int(_id) for _id in ids]}})
        self.write(res)


class ListHandler(BaseHandler):
    """
        日志列表
        post -> /log/list/
    """

    @authenticated_async(['admin', 'super'])
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
            query_criteria["$or"] = [{"username": re.compile(search_key)}, {"uri": re.compile(search_key)},
                                     {"ip": re.compile(search_key)}]

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Log.collection_name, query_criteria, [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Log.collection_name, query_criteria)

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
