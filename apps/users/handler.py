import json
import re

from apps.users.forms import UserForm
from apps.users.models import User
from apps.users.service import UserService
from bases import utils
from bases.decorators import authenticated_admin_async
from bases.handler import BaseHandler
from bases.res import resFunc
from bases.utils import get_md5, get_random_head


# 添加
class AddHandler(BaseHandler):
    '''
        post -> /user/add/
        payload:
            {
                "name": "昵称",
                "username": "用户名",
                "email": "邮箱",
                "gender": "性别",
                "password": "密码",
                "roles": "角色列表",
                "status": "状态"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = UserForm.from_json(data)
        name = form.name.data
        username = form.username.data
        email = form.email.data
        gender = form.gender.data
        password = form.password.data
        roles = form.roles.data
        status = form.status.data

        user_db = User()

        # 查找账号是否存在
        user = await user_db.find_one({"username": username})
        if user is not None:
            res['code'] = 50000
            res['message'] = '该账号已存在'
            self.write(json.dumps(res))
            return

        # 判断邮箱是否存在
        user = await user_db.find_one({"email": email})
        if user is not None:
            res['code'] = 50000
            res['message'] = '该邮箱已存在'
            self.write(json.dumps(res))
            return

        # 新增
        user_db.name = name
        user_db.username = username
        user_db.email = email
        user_db.gender = gender
        user_db.password = get_md5(password)
        user_db.has_password = 1
        user_db.status = status
        user_db.avatar = get_random_head()
        user_db.roles = roles
        await user_db.insert_one(user_db.get_add_json())

        self.write(json.dumps(res))


# 删除
class Deletehandler(BaseHandler):
    '''
        post -> /user/delete/
        payload:
            {
                "id": "用户编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = UserForm.from_json(data)
        _id = form.id.data
        # 删除数据
        user_db = User()
        await user_db.delete_one({"_id": _id})
        # 删除缓存
        UserService.delete_cache(_id)
        self.write(json.dumps(res))


# 修改
class UpdateHandler(BaseHandler):
    '''
        post -> /user/update/
        payload:
            {
                "id": "用户编号",
                "name": "昵称",
                "gender": "性别",
                "status": "状态 1正常 2注销",
                "roles": "角色列表",
                "password": "密码"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = UserForm.from_json(data)
        _id = form.id.data
        name = form.name.data
        gender = form.gender.data
        status = form.status.data
        roles = form.roles.data
        password = form.password.data

        user_db = User()

        # 修改数据
        await user_db.update_one({"_id": _id},
                                 {"$set": {"name": name, "gender": gender, "status": status,
                                           "roles": roles}})
        # 修改密码
        if password is not None:
            await user_db.update_one({"_id": _id}, {"$set": {"password": get_md5(password)}})
        # 删除缓存
        UserService.delete_cache(_id)
        self.write(json.dumps(res))


# 列表
class ListHandler(BaseHandler):
    '''
       post -> /user/list/
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
        res = resFunc([])
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = UserForm.from_json(data)
        current_page = form.currentPage.data
        page_size = form.pageSize.data
        search_key = form.searchKey.data
        status = form.status.data
        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}, "username": {"$ne": "000"}}
        if search_key is not None:
            query_criteria["$or"] = [{"name": re.compile(search_key)}, {"username": re.compile(search_key)}]
        if status is not None:
            query_criteria["status"] = status
        user_db = User()
        # 查询分页
        query = await user_db.find_page(page_size, current_page, [("_id", -1)], query_criteria)

        # 查询总数
        total = await user_db.query_count(query)
        pages = utils.get_pages(total, page_size)

        results = []
        for item in query:
            item['password'] = ""
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

