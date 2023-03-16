import json
import re

from apps.tasks.forms import TaskForm
from apps.tasks.models import Task
from bases import utils
from bases.decorators import authenticated_admin_async
from bases.handler import BaseHandler
from bases.res import resFunc
from bases.utils import show_error_log


# 添加
class AddHandler(BaseHandler):
    '''
        post -> /task/add/
        payload:
            {
                "name": "任务名称",
                "func": "执行方法",
                "type": "任务类型 1定时任务 2周期任务",
                "exec_data": "定时任务执行时间",
                "exec_cron": "周期任务执行时间",
                "exec_interval": "间隔任务执行时间"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = TaskForm.from_json(data)
        name = form.name.data
        func = form.func.data
        _type = form.type.data
        exec_data = form.exec_data.data
        exec_cron = form.exec_cron.data
        exec_interval = form.exec_interval.data

        task_db = Task()
        task_db.name = name
        task_db.func = func
        task_db.type = _type
        task_db.exec_data = exec_data
        task_db.exec_cron = exec_cron
        task_db.exec_interval = exec_interval

        await task_db.insert_one(task_db.get_add_json())

        self.write(json.dumps(res))


# 删除
class DeleteHandler(BaseHandler):
    '''
        post -> /task/delete/
        payload:
            {
                "id": "任务编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = TaskForm.from_json(data)
        _id = form.id.data

        task_db = Task()
        # 删除数据
        await task_db.delete_one({"_id": _id})
        self.write(json.dumps(res))


# 修改
class UpdateHandler(BaseHandler):
    '''
        post -> /task/update/
        payload:
            {
                "id": "用户编号",
                "name": "任务名称",
                "func": "执行方法",
                "type": "任务类型 1定时任务 2周期任务 3间隔任务",
                "exec_data": "定时任务执行时间",
                "exec_cron": "周期任务执行时间",
                "exec_interval": "间隔任务执行时间"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = TaskForm.from_json(data)
        _id = form.id.data
        name = form.name.data
        func = form.func.data
        _type = form.type.data
        exec_data = form.exec_data.data
        exec_cron = form.exec_cron.data
        exec_interval = form.exec_interval.data

        task_db = Task()
        # 修改数据
        await task_db.update_one({"_id": _id}, {
            "$set": {"name": name, "func": func, "type": _type,
                     "exec_data": exec_data, "exec_cron": exec_cron, "exec_interval": exec_interval, "status": 0}})
        self.write(json.dumps(res))


# 列表
class ListHandler(BaseHandler):
    '''
       post -> /task/list/
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
        form = TaskForm.from_json(data)
        current_page = form.currentPage.data
        page_size = form.pageSize.data
        search_key = form.searchKey.data
        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["$or"] = [{"name": re.compile(search_key)}]
        task_db = Task()
        # 查询分页
        query = await task_db.find_page(page_size, current_page, [("_id", -1)], query_criteria)

        # 查询总数
        total = await task_db.query_count(query)
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


# 开启任务
class StartTaskHandler(BaseHandler):
    '''
        post -> /task/start/
        payload:
            {
                "id": "任务编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = TaskForm.from_json(data)
        _id = form.id.data

        task_db = Task()
        task = await task_db.find_one({"_id": _id})
        if task is not None:
            if task['status'] != 1:
                if task['type'] == 1:
                    # 定时任务类型
                    self.application.scheduler.add_job(task['func'], 'date', run_date=task['exec_data'], id=str(_id),
                                                       args=[str(_id)])
                elif task['type'] == 2:
                    # 周期任务类型
                    exec_cron = task['exec_cron']
                    hour = exec_cron[0:2]
                    minute = exec_cron[3:5]
                    self.application.scheduler.add_job(task['func'], 'cron', hour=int(hour),
                                                       minute=int(minute), id=str(_id),
                                                       args=[str(_id)])
                elif task['type'] == 3:
                    # 间隔任务类型
                    seconds = task['exec_interval']
                    self.application.scheduler.add_job(task['func'], 'interval', seconds=int(seconds),
                                                       id=str(_id),
                                                       args=[str(_id)])
                # 修改数据状态
                await task_db.update_one({"_id": _id}, {"$set": {"status": 1}})
        self.write(json.dumps(res))


# 停止任务
class EndTaskHandler(BaseHandler):
    '''
        post -> /task/end/
        payload:
            {
                "id": "任务编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = TaskForm.from_json(data)
        _id = form.id.data

        task_db = Task()
        task = await task_db.find_one({"_id": _id})
        if task is not None:
            if task['status'] == 1:
                try:
                    # 结束任务
                    self.application.scheduler.remove_job(str(_id))
                except Exception as e:
                    show_error_log(e)
                # 修改数据状态
                await task_db.update_one({"_id": _id}, {"$set": {"status": 2}})
        self.write(json.dumps(res))
