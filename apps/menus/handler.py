import json

from apps.menus.forms import MenuForm
from apps.menus.models import Menu
from bases.decorators import authenticated_admin_async, authenticated_async
from bases.handler import BaseHandler
from bases.res import resFunc


# 添加
class AddHandler(BaseHandler):
    '''
        post -> /menu/add/
        payload:
            {
                "pid": "父ID",
                "name": "名称",
                "icon": "图标",
                "url": "地址",
                "roles"： "角色",
                "level": "层级",
                "sort": "排序",
                "status": "状态"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = MenuForm.from_json(data)
        pid = form.pid.data
        name = form.name.data
        icon = form.icon.data
        url = form.url.data
        roles = form.roles.data
        level = form.level.data
        sort = form.sort.data
        status = form.status.data

        menu_db = Menu()
        menu_db.pid = pid
        menu_db.name = name
        menu_db.icon = icon
        menu_db.url = url
        menu_db.roles = roles
        menu_db.level = level
        menu_db.sort = sort
        menu_db.status = status
        await menu_db.insert_one(menu_db.get_add_json())
        self.write(res)


# 删除
class DeleteHandler(BaseHandler):
    '''
        post -> /menu/delete/
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
        form = MenuForm.from_json(data)
        _id = form.id.data
        # 删除数据
        menu_db = Menu()
        await menu_db.delete_one({"_id": _id})
        self.write(res)


# 修改
class UpdateHandler(BaseHandler):
    '''
        post -> /menu/update/
        payload:
            {
                "id": "编号",
                "name": "名称",
                "icon": "图标",
                "url": "地址",
                "roles"： "角色",
                "sort": "排序",
                "status": "状态"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = MenuForm.from_json(data)
        _id = form.id.data
        name = form.name.data
        icon = form.icon.data
        url = form.url.data
        roles = form.roles.data
        sort = form.sort.data
        status = form.status.data
        # 修改数据
        menu_db = Menu()
        await menu_db.update_one({"_id": _id},
                                 {"$set": {"name": name, "icon": icon, "url": url, "roles": roles, "sort": sort,
                                           "status": status}})
        self.write(res)


# 列表
class ListHandler(BaseHandler):
    '''
       get -> /menu/list/
    '''

    @authenticated_admin_async
    async def get(self):
        res = resFunc([])
        menu_db = Menu()
        # 查询一级菜单
        query_criteria = {"pid": 0}
        query_one = await menu_db.find_all(query_criteria)
        query_one = await menu_db.query_sort(query_one, [("sort", -1), ("_id", -1)])

        results = []
        for one in query_one:
            one["id"] = one["_id"]
            results.append(one)
            # 查询二级菜单
            query_two = await menu_db.find_all({"pid": one["_id"]})
            query_two = await menu_db.query_sort(query_two, [("sort", -1), ("_id", -1)])
            for two in query_two:
                two["id"] = two["_id"]
                results.append(two)
        res['data'] = results
        self.write(res)


# 所有列表
class GetListHandler(BaseHandler):
    '''
       get -> /menu/getList/
    '''

    @authenticated_async
    async def get(self):
        res = resFunc([])

        current_user = self.current_user

        menu_db = Menu()
        # 查询一级菜单
        query_criteria = {"pid": 0, "status": 1, "roles": {"$in": current_user["roles"]}}
        query_one = await menu_db.find_all(query_criteria)
        query_one = await menu_db.query_sort(query_one, [("sort", -1), ("_id", -1)])

        results = []
        for one in query_one:
            # 查询二级菜单
            query_two = await menu_db.find_all({"pid": one["_id"], "status": 1, "roles": {"$in": current_user["roles"]}})
            query_two = await menu_db.query_sort(query_two, [("sort", -1), ("_id", -1)])
            children = []
            for two in query_two:
                children.append({"text": two["name"], "value": two["url"], "icon": two.get("icon")})
            results.append({"text": one["name"], "value": one["url"], "icon": one.get("icon"), "children": children})
        res['data'] = results
        self.write(res)
