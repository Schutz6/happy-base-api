import json
import re

from apps.roles.forms import RoleForm
from apps.roles.models import Role
from bases import utils
from bases.decorators import authenticated_admin_async
from bases.handler import BaseHandler
from bases.res import resFunc


# 添加
class AddHandler(BaseHandler):
    '''
        post -> /role/add/
        payload:
            {
                "name": "唯一ID",
                "describe": "角色",
                "remarks": "备注",
                "sort": "排序"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = RoleForm.from_json(data)
        name = form.name.data
        describe = form.describe.data
        remarks = form.remarks.data
        sort = form.sort.data
        # 查找角色是否存在
        role_db = Role()
        role = await role_db.find_one({"name": name})
        if role is not None:
            res['code'] = 50000
            res['message'] = '该唯一ID已存在'
        else:
            role_db.name = name
            role_db.describe = describe
            role_db.remarks = remarks
            role_db.sort = sort
            await role_db.insert_one(role_db.get_add_json())
        self.write(res)


# 删除
class DeleteHandler(BaseHandler):
    '''
        post -> /role/delete/
        payload:
            {
                "id": "角色编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = RoleForm.from_json(data)
        _id = form.id.data
        # 删除数据
        role_db = Role()
        await role_db.delete_one({"_id": _id})
        self.write(res)


# 修改
class UpdateHandler(BaseHandler):
    '''
        post -> /role/update/
        payload:
            {
                "id": "用户编号",
                "name": "唯一ID",
                "describe": "角色",
                "remarks": "备注"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = RoleForm.from_json(data)
        _id = form.id.data
        name = form.name.data
        describe = form.describe.data
        remarks = form.remarks.data
        sort = form.sort.data
        # 修改数据
        role_db = Role()
        await role_db.update_one({"_id": _id},
                                 {"$set": {"name": name, "describe": describe, "remarks": remarks, "sort": sort}})
        self.write(res)


# 列表
class ListHandler(BaseHandler):
    '''
       post -> /role/list/
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
        form = RoleForm.from_json(data)
        current_page = form.currentPage.data
        page_size = form.pageSize.data
        search_key = form.searchKey.data
        role_db = Role()
        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["$or"] = [{"name": re.compile(search_key)}, {"describe": re.compile(search_key)}]
        # 查询分页
        query = await role_db.find_page(page_size, current_page, [("sort", -1), ("_id", -1)], query_criteria)

        # 查询总数
        total = await role_db.query_count(query)
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


# 所有列表
class GetListHandler(BaseHandler):
    '''
       get -> /role/getList/
    '''

    @authenticated_admin_async
    async def get(self):
        res = resFunc([])

        current_user = self.current_user

        role_db = Role()
        query = await role_db.find_all({"_id": {"$ne": "sequence_id"}})
        query = await role_db.query_sort(query, [("sort", -1), ("_id", -1)])
        results = []
        if 'superadmin' in current_user["roles"]:
            for item in query:
                # 全部角色
                obj = {"value": item["name"], "text": item["describe"]}
                results.append(obj)
        elif 'admin' in current_user["roles"]:
            for item in query:
                # 过滤超管角色
                if item["name"] != 'superadmin':
                    obj = {"value": item["name"], "text": item["describe"]}
                    results.append(obj)
        res['data'] = results
        self.write(res)
