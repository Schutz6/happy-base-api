import json
import re

from apps.logs.func import async_clear_log
from apps.logs.forms import LogForm
from apps.logs.models import Log
from bases import utils
from bases.decorators import authenticated_admin_async
from bases.handler import BaseHandler
from bases.res import resFunc


class ClearHandler(BaseHandler):
    '''
        清空日志
        get -> /log/clear/
    '''

    @authenticated_admin_async
    async def get(self):
        res = resFunc({})
        # 清空日志(异步方法)
        async_clear_log()
        self.write(res)


class BatchDeleteHandler(BaseHandler):
    '''
        批量删除
        post -> /log/batchDelete/
        payload:
           {
                "ids": "多选ID"
           }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = LogForm.from_json(data)
        ids = form.ids.data
        # 批量删除
        log_db = Log()
        log_db.delete_many({"_id": {"$in": [int(_id) for _id in ids]}})
        self.write(res)


class ListHandler(BaseHandler):
    '''
        日志列表
        post -> /log/list/
        payload:
           {
               "currentPage": 1,
               "pageSize": 10,
               "searchKey": "关键字",
           }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = LogForm.from_json(data)
        current_page = form.currentPage.data
        page_size = form.pageSize.data
        search_key = form.searchKey.data
        log_db = Log()
        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["$or"] = [{"username": re.compile(search_key)}, {"uri": re.compile(search_key)},
                                     {"ip": re.compile(search_key)}]
        # 查询分页
        query = log_db.find_page(page_size, current_page, [("_id", -1)], query_criteria)

        # 查询总数
        total = log_db.query_count(query)
        pages = utils.get_pages(total, page_size)

        results = []
        for item in query:
            item["id"] = item["_id"]
            results.append(item)

        data = {
            "total": total,
            "pages": pages,
            "size": page_size,
            "current": current_page,
            "results": results
        }

        res['data'] = data
        self.write(res)
