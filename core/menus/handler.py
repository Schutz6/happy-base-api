import json

from core.menus.models import Menu
from core.menus.service import MenuService
from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func
from base.utils import mongo_helper


class AddHandler(BaseHandler):
    """
        添加
        post -> /menu/add/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)

        # 入库
        await mongo_helper.insert_one(Menu.collection_name, await Menu.get_json(req_data))
        # 删除缓存
        MenuService.remove_menus()
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /menu/delete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            # 删除数据
            await mongo_helper.delete_one(Menu.collection_name, {"_id": _id})
            # 删除缓存
            MenuService.remove_menus()
        self.write(res)


class UpdateHandler(BaseHandler):
    """
        修改
        post -> /menu/update/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        name = req_data.get("name")
        icon = req_data.get("icon")
        url = req_data.get("url")
        roles = req_data.get("roles", [])
        sort = req_data.get("sort", 0)
        status = req_data.get("status", 0)

        if _id is not None:
            # 修改数据
            await mongo_helper.update_one(Menu.collection_name, {"_id": _id},
                                          {"$set": {"name": name, "icon": icon, "url": url, "roles": roles,
                                                    "sort": sort,
                                                    "status": status}})
            # 删除缓存
            MenuService.remove_menus()
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        get -> /menu/list/
    """

    @authenticated_async(['admin', 'super'])
    async def get(self):
        res = res_func([])
        # 查询一级菜单
        query_one = await mongo_helper.fetch_all(Menu.collection_name, {"pid": 0}, [("sort", -1), ("_id", -1)])

        results = []
        for one in query_one:
            one["id"] = one["_id"]
            results.append(one)
            # 查询二级菜单
            query_two = await mongo_helper.fetch_all(Menu.collection_name, {"pid": one["_id"]},
                                                     [("sort", -1), ("_id", -1)])
            for two in query_two:
                two["id"] = two["_id"]
                results.append(two)
        res['data'] = results
        self.write(res)


class GetListHandler(BaseHandler):
    """
        所有列表
        get -> /menu/getList/
    """

    @authenticated_async(None)
    async def get(self):
        res = res_func([])
        current_user = self.current_user
        res['data'] = await MenuService.get_menus(current_user["roles"])
        self.write(res)
