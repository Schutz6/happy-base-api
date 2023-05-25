import json
import re

from apps.tasks.func import run_task
from apps.tasks.models import Task
from bases.decorators import authenticated_async
from bases.handler import BaseHandler
from bases.res import res_func
from bases.utils import mongo_helper, show_error_log


class AddHandler(BaseHandler):
    """
        添加
        post -> /task/add/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)

        await mongo_helper.insert_one(Task.collection_name, await Task.get_json(req_data))
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /task/delete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        if _id is not None:
            # 删除数据
            await mongo_helper.delete_one(Task.collection_name, {"_id": _id})
        self.write(res)


class UpdateHandler(BaseHandler):
    """
        修改
        post -> /task/update/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        name = req_data.get("name")
        func = req_data.get("func")
        _type = req_data.get("type")
        exec_cron = req_data.get("exec_cron")
        exec_interval = req_data.get("exec_interval")
        options = req_data.get("options")

        if _id is not None:
            # 修改数据
            await mongo_helper.update_one(Task.collection_name, {"_id": _id},
                                          {"$set": {"name": name, "func": func, "type": _type,
                                                    "exec_cron": exec_cron, "exec_interval": exec_interval, "status": 0,
                                                    "options": options}})
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /task/list/
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
            query_criteria["$or"] = [{"name": re.compile(search_key)}]

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Task.collection_name, query_criteria, [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Task.collection_name, query_criteria)

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


class StartTaskHandler(BaseHandler):
    """
        开启任务
        post -> /task/start/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            task = await mongo_helper.fetch_one(Task.collection_name, {"_id": _id})
            if task is not None:
                if task['status'] != 1:
                    try:
                        # 启动任务
                        run_task(self.application.scheduler, task)
                        # 修改数据状态
                        await mongo_helper.update_one(Task.collection_name, {"_id": _id}, {"$set": {"status": 1}})
                    except Exception as e:
                        show_error_log(e)
        self.write(res)


class EndTaskHandler(BaseHandler):
    """
        停止任务
        post -> /task/end/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            task = await mongo_helper.fetch_one(Task.collection_name, {"_id": _id})
            if task is not None:
                if task['status'] == 1:
                    # 修改数据状态
                    await mongo_helper.update_one(Task.collection_name, {"_id": _id}, {"$set": {"status": 2}})
                    try:
                        # 结束任务
                        self.application.scheduler.remove_job(str(_id))
                    except Exception as e:
                        show_error_log(e)
        self.write(res)
