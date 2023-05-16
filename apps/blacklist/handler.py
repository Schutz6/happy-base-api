import json
import re

from bson import ObjectId
from apps.blacklist.models import Blacklist
from apps.blacklist.service import BlacklistService
from bases.decorators import authenticated_async
from bases.handler import BaseHandler
from bases.res import res_func
from bases.utils import mongo_helper


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /blacklist/delete/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            # 查询
            blacklist = await mongo_helper.fetch_one(Blacklist.collection_name, {"_id": ObjectId(_id)})
            if blacklist is not None:
                # 删除数据
                await BlacklistService.remove_ip_blacklist(blacklist["ip"])
        self.write(res)


class BatchDeleteHandler(BaseHandler):
    """
        批量删除
        post -> /blacklist/batchDelete/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        ids = req_data.get("ids")

        if ids is not None:
            for _id in ids:
                # 查询
                blacklist = await mongo_helper.fetch_one(Blacklist.collection_name, {"_id": ObjectId(_id)})
                if blacklist is not None:
                    # 删除数据
                    await BlacklistService.remove_ip_blacklist(blacklist["ip"])
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /blacklist/list/
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
        query_criteria = {}
        if search_key is not None:
            query_criteria["$or"] = [{"ip": re.compile(search_key)}]

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Blacklist.collection_name, query_criteria, [("add_time", -1)],
                                                       page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Blacklist.collection_name, query_criteria)

        results = []
        for item in page_data.get("list", []):
            item["id"] = str(item["_id"])
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
