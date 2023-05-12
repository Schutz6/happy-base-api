import json
import re

from apps.roles.models import Role
from bases.decorators import authenticated_async
from bases.handler import BaseHandler
from bases.res import res_func
from bases.utils import mongo_helper


class AddHandler(BaseHandler):
    """
        添加
        post -> /role/add/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        name = req_data.get("name")

        # 查找角色是否存在
        role = await mongo_helper.fetch_one(Role.collection_name, {"name": name})
        if role is not None:
            res['code'] = 50000
            res['message'] = '该唯一ID已存在'
        else:
            await mongo_helper.insert_one(Role.collection_name, await Role.get_json(req_data))
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /role/delete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            # 删除数据
            await mongo_helper.delete_one(Role.collection_name, {"_id": _id})
        self.write(res)


class UpdateHandler(BaseHandler):
    """
        修改
        post -> /role/update/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        name = req_data.get("name")
        describe = req_data.get("describe")
        remarks = req_data.get("remarks")
        sort = req_data.get("sort", 0)

        if _id is not None:
            role = await mongo_helper.fetch_one(Role.collection_name, {"_id": _id})
            if role is not None:
                if role["name"] != name:
                    # 角色ID发生变化，判断是否存在
                    role = await mongo_helper.fetch_one(Role.collection_name, {"name": name})
                    if role is not None:
                        res['code'] = 50000
                        res['message'] = '该唯一ID已存在'
                        self.write(res)
                        return
                # 修改数据
                await mongo_helper.update_one(Role.collection_name, {"_id": _id},
                                              {"$set": {"name": name, "describe": describe, "remarks": remarks,
                                                        "sort": sort}})
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /role/list/
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
            query_criteria["$or"] = [{"name": re.compile(search_key)}, {"describe": re.compile(search_key)}]

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Role.collection_name, query_criteria,
                                                       [("sort", -1), ("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Role.collection_name, query_criteria)

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
        get -> /role/getList/
    """

    @authenticated_async(['admin', 'super'])
    async def get(self):
        res = res_func({})

        current_user = self.current_user

        query = await mongo_helper.fetch_all(Role.collection_name, {"_id": {"$ne": "sequence_id"}},
                                             [("sort", -1), ("_id", -1)])
        results = []
        if 'super' in current_user["roles"]:
            for item in query:
                # 全部角色
                obj = {"value": item["name"], "text": item["describe"]}
                results.append(obj)
        elif 'admin' in current_user["roles"]:
            for item in query:
                # 过滤超管角色
                if item["name"] != 'super':
                    obj = {"value": item["name"], "text": item["describe"]}
                    results.append(obj)
        res['data'] = results
        self.write(res)
