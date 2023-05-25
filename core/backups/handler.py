import json
import os
import time

from core.backups.models import Backup
from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func
from base.utils import mongo_helper
from config import settings


class DumpHandler(BaseHandler):
    """
        备份数据库
        post -> /backup/dump/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        time_path = time.strftime("%Y%m%d%H%M%S", time.localtime())
        backup_path = os.path.join(os.path.dirname(__file__), settings['BACKUP_URL'], time_path)
        os.system("mongodump -h 127.0.0.1 -d " + settings["mongo"]["database"] + " -o " + backup_path)
        directory = os.path.join(backup_path, settings["mongo"]["database"])
        # 添加到备份库
        await mongo_helper.insert_one(Backup.collection_name, await Backup.get_json({"directory": directory}))
        self.write(res)


class RestoreHandler(BaseHandler):
    """
        恢复数据库
        post -> /backup/restore/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        if _id is not None:
            backup = await mongo_helper.fetch_one(Backup.collection_name, {"_id": _id})
            if backup is not None:
                os.system(
                    "mongorestore -h 127.0.0.1 -d " + settings["mongo"]["database"] + " --drop " + backup["directory"])
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /backup/delete/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            # 删除数据
            await mongo_helper.delete_one(Backup.collection_name, {"_id": _id})
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /backup/list/
    """

    @authenticated_async(['super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)

        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Backup.collection_name, query_criteria,
                                                       [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Backup.collection_name, query_criteria)

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
