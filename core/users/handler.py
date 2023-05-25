import json
import re

from core.users.models import User
from core.users.service import UserService
from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func
from config import settings
from base.utils import get_md5, mongo_helper, get_random_head


class AddHandler(BaseHandler):
    """
        添加
        post -> /user/add/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        username = req_data.get("username")

        # 查找账号是否存在
        user = await mongo_helper.fetch_one(User.collection_name, {"username": username})
        if user is not None:
            res['code'] = 50000
            res['message'] = '该账号已存在'
            self.write(res)
            return

        # 新增
        req_data["avatar"] = get_random_head()
        req_data["password"] = get_md5(req_data["password"])
        await mongo_helper.insert_one(User.collection_name, await User.get_json(req_data))
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /user/delete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            # 删除数据
            await mongo_helper.delete_one(User.collection_name, {"_id": _id})
            # 删除缓存
            UserService.delete_cache(_id)
        self.write(res)


class BatchDeleteHandler(BaseHandler):
    """
        批量删除
        post -> /user/batchDelete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        ids = req_data.get("ids")
        if ids is not None:
            ids = [int(_id) for _id in ids]
            # 批量删除
            await mongo_helper.delete_many(User.collection_name, {"_id": {"$in": ids}})
            for _id in ids:
                # 删除缓存
                UserService.delete_cache(_id)
        self.write(res)


class UpdateHandler(BaseHandler):
    """
        修改
        post -> /user/update/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        name = req_data.get("name")
        gender = req_data.get("gender")
        password = req_data.get("password")
        roles = req_data.get("roles", [])
        status = req_data.get("status", 0)
        avatar = req_data.get("avatar")

        if _id is not None:
            # 修改数据
            await mongo_helper.update_one(User.collection_name, {"_id": _id},
                                          {"$set": {"name": name, "gender": gender, "status": status,
                                                    "roles": roles}})
            # 修改密码
            if password is not None:
                await mongo_helper.update_one(User.collection_name, {"_id": _id},
                                              {"$set": {"password": get_md5(password)}})
            # 修改头像
            if avatar is not None:
                avatar = avatar.replace(settings['SITE_URL'], "")
                await mongo_helper.update_one(User.collection_name, {"_id": _id}, {"$set": {"avatar": avatar}})
            # 删除缓存
            UserService.delete_cache(_id)
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /user/list/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func([])
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)
        search_key = req_data.get("searchKey")
        status = req_data.get("status")
        roles = req_data.get("roles", [])

        current_user = self.current_user

        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if len(roles) == 0:
            # 查询角色
            roles = ["user"]
            if 'admin' in current_user["roles"]:
                roles.append("admin")
            if 'super' in current_user["roles"]:
                roles.append("admin")
                roles.append("super")
        query_criteria["roles"] = {"$in": roles}
        if search_key is not None:
            query_criteria["$or"] = [{"name": re.compile(search_key)}, {"username": re.compile(search_key)}]
        if status is not None:
            query_criteria["status"] = status

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(User.collection_name, query_criteria, [("_id", -1)],
                                                       page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(User.collection_name, query_criteria)

        results = []
        for item in page_data.get("list", []):
            item['password'] = ""
            item["id"] = item["_id"]
            item["avatar"] = settings['SITE_URL'] + item["avatar"]
            results.append(item)

        data = {
            "total": total,
            "size": page_size,
            "current": current_page,
            "results": results
        }

        res['data'] = data
        self.write(res)
