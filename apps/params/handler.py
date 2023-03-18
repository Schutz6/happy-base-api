import json
import re

from apps.params.forms import ParamForm
from apps.params.models import Param
from bases import utils
from bases.decorators import authenticated_admin_async, log_async
from bases.handler import BaseHandler
from bases.res import resFunc


# 添加
class AddHandler(BaseHandler):
    '''
        post -> /param/add/
        payload:
            {
                "key": "唯一ID",
                "value": "参数值",
                "remarks": "备注",
                "status": "状态"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = ParamForm.from_json(data)
        key = form.key.data
        value = form.value.data
        remarks = form.remarks.data
        status = form.status.data
        # 查找是否存在
        param_db = Param()
        param = await param_db.find_one({"key": key})
        if param is not None:
            res['code'] = 50000
            res['message'] = '该唯一ID已存在'
        else:
            param_db.key = key
            param_db.value = value
            param_db.remarks = remarks
            param_db.status = status
            await param_db.insert_one(param_db.get_add_json())
        self.write(json.dumps(res))


# 删除
class DeleteHandler(BaseHandler):
    '''
        post -> /param/delete/
        payload:
            {
                "id": "编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = ParamForm.from_json(data)
        _id = form.id.data
        # 删除数据
        param_db = Param()
        await param_db.delete_one({"_id": _id})
        self.write(json.dumps(res))


# 修改
class UpdateHandler(BaseHandler):
    '''
        post -> /param/update/
        payload:
            {
                "id": "编号",
                "value": "参数值",
                "remarks": "备注",
                "status": "状态"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = ParamForm.from_json(data)
        _id = form.id.data
        value = form.value.data
        remarks = form.remarks.data
        status = form.status.data
        # 修改数据
        param_db = Param()
        await param_db.update_one({"_id": _id},
                                  {"$set": {"value": value, "remarks": remarks, "status": status}})
        self.write(json.dumps(res))


# 列表
class ListHandler(BaseHandler):
    '''
       post -> /param/list/
       payload:
           {
               "currentPage": 1,
               "pageSize": 10,
               "searchKey": "关键字",
               "status": "状态"
           }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = ParamForm.from_json(data)
        current_page = form.currentPage.data
        page_size = form.pageSize.data
        search_key = form.searchKey.data
        status = form.status.data

        param_db = Param()
        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["$or"] = [{"key": re.compile(search_key)}, {"value": re.compile(search_key)},
                                     {"remarks": re.compile(search_key)}]
        if status is not None:
            query_criteria["status"] = status
        # 查询分页
        query = await param_db.find_page(page_size, current_page, [("_id", -1)], query_criteria)

        # 查询总数
        total = await param_db.query_count(query)
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
        self.write(json.dumps(res))


# 所有列表
class GetListHandler(BaseHandler):
    '''
       get -> /param/getList/
    '''

    @log_async
    async def get(self):
        res = resFunc({})
        param_db = Param()
        query = await param_db.find_all({"status": 0})
        results = []
        for item in query:
            results.append((item["key"], item["value"]))
        res['data'] = dict(results)
        self.write(json.dumps(res))
