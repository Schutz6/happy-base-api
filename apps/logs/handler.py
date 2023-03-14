import json
import re

from apps.logs.forms import LogForm
from apps.logs.models import Log
from bases import utils
from bases.decorators import authenticated_async
from bases.handler import BaseHandler
from bases.res import resFunc


# 清空日志
class ClearHandler(BaseHandler):
    '''
        get -> /log/clear/
    '''

    @authenticated_async
    async def get(self):
        res = resFunc({})
        # 清空日志
        log_db = Log()
        await log_db.delete_many({})
        self.write(res)


# 日志列表
class ListHandler(BaseHandler):
    '''
       post -> /log/list/
       payload:
           {
               "currentPage": 1,
               "pageSize": 10,
               "searchKey": "关键字",
           }
    '''

    @authenticated_async
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
        query = await log_db.find_page(page_size, current_page, [("_id", -1), ("add_time", -1)], query_criteria)

        # 查询总数
        total = await log_db.query_count(query)
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
        self.write(json.dumps(res, default=utils.json_serial))
