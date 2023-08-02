import json
import jwt

from datetime import datetime
from core.users.models import User
from core.users.service import UserService
from base.decorators import authenticated_async, log_async
from base.handler import BaseHandler
from base.res import res_func
from config import settings
from base.utils import get_md5, now_utc, mongo_helper


class LoginHandler(BaseHandler):
    """
        用户登录
        post -> /login/
    """

    @log_async
    async def post(self):
        channel = self.request.headers.get('Channel', 'default')
        res = res_func({})
        res['data'] = {"token": ""}
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        area = req_data.get("area")
        username = req_data.get("username")
        password = req_data.get("password")

        # 判断是否邮箱
        if username.find("@") > -1:
            user = await mongo_helper.fetch_one(User.collection_name, {"email": username})
        else:
            if area is not None:
                user = await mongo_helper.fetch_one(User.collection_name, {"area": area, "mobile": username})
            else:
                user = await mongo_helper.fetch_one(User.collection_name, {"username": username})
        if user is not None:
            # 判断密码错误次数
            login_error_count = UserService.get_login_error_count(user["_id"])
            if login_error_count >= 5:
                res['code'] = 100061
                res['message'] = '账号已锁定'
                self.write(res)
                return
            # 判断是否已设置密码
            if user['has_password'] == 0:
                res['code'] = 10024
                res['message'] = '未设置密码'
                self.write(res)
                return
            # 对比密码是否正确
            if user['password'] == get_md5(password):
                # 判断账号是否正常
                if user['status'] == "1":
                    payload = {
                        'id': user['_id'],
                        'username': user['username'],
                        'exp': datetime.utcnow()
                    }
                    token = jwt.encode(payload=payload, key=settings["secret_key"], algorithm='HS256')
                    res['data'] = {"token": token}
                    # 存储用户令牌
                    UserService.save_login_token(user["_id"], channel, token)
                    # 登录成功之后，删除错误次数
                    UserService.delete_login_error_cache(user["_id"])
                else:
                    res['code'] = 10005
                    res['message'] = '用户不存在'
            else:
                res['code'] = 10006
                res['message'] = '密码错误'
                # 记录错误次数 5次之后锁定30分钟
                UserService.add_login_error_count(user["_id"])
        else:
            res['code'] = 10005
            res['message'] = '用户不存在'
        self.write(res)


class UserHandler(BaseHandler):
    """
        读取用户资料
        get -> /user/
    """

    @authenticated_async(None)
    async def get(self):
        res = res_func({})
        current_user = self.current_user
        current_user["id"] = current_user["_id"]
        current_user["avatar"] = current_user["avatar"].replace("#URL#", settings['SITE_URL'])
        res['data'] = current_user

        # 更新登录信息
        await mongo_helper.update_one(User.collection_name, {"_id": current_user["_id"]}, {
            "$set": {"last_time": now_utc(), "last_ip": self.request.remote_ip}})
        self.write(res)

    """
        部分更新用户资料
        post -> /user/
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        user = self.current_user
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)

        gender = req_data.get("gender")
        if gender is not None:
            await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]}, {"$set": {"gender": gender}})
        introduction = req_data.get("introduction")
        if introduction is not None:
            await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]},
                                          {"$set": {"introduction": introduction}})
        birthday = req_data.get("birthday")
        if birthday is not None:
            await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]}, {"$set": {"birthday": birthday}})
        address = req_data.get("address")
        if address is not None:
            await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]}, {"$set": {"address": address}})
        name = req_data.get("name")
        if name is not None:
            await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]}, {"$set": {"name": name}})
        avatar = req_data.get("avatar")
        if avatar is not None:
            # 替换地址
            avatar = avatar.replace(settings['SITE_URL'], "#URL#")
            await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]}, {"$set": {"avatar": avatar}})

        # 删除缓存
        UserService.delete_cache(user["_id"])
        self.write(res)


class LogoutHandler(BaseHandler):
    """
        退出登录
        get -> /logout/
    """

    @authenticated_async(None)
    async def get(self):
        res = res_func({})
        channel = self.request.headers.get('Channel', 'default')
        current_user = self.current_user
        if current_user is not None:
            UserService.remove_login_token(current_user["_id"], channel)
        res["message"] = "成功退出"
        self.write(res)


class ChangePwdHandler(BaseHandler):
    """
        修改用户密码
        post -> /changePwd/
        payload:
            {
                "type": "类型 1登录密码 2支付密码",
                "oldPassword": "旧密码"
                "newPassword": "新密码"
            }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        current_user = self.current_user
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _type = req_data.get("type")
        old_password = req_data.get("oldPassword")
        new_password = req_data.get("newPassword")
        user = await mongo_helper.fetch_one(User.collection_name, {"_id": current_user["_id"]})
        if user is not None:
            if _type == 1:
                # 判断是否第一次修改密码
                if user["has_password"] == 1:
                    if user["password"] != get_md5(old_password):
                        res['code'] = 10006
                        res['message'] = '密码错误'
                    else:
                        await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]},
                                                      {"$set": {"password": get_md5(new_password)}})
                else:
                    await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]},
                                                  {"$set": {"password": get_md5(new_password), "has_password": 1}})
            elif _type == 2:
                # 判断是否第一次修改密码
                if user["has_pay_password"] == 1:
                    if user["pay_password"] != get_md5(old_password):
                        res['code'] = 10006
                        res['message'] = '密码错误'
                    else:
                        await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]},
                                                      {"$set": {"pay_password": get_md5(new_password)}})
                else:
                    await mongo_helper.update_one(User.collection_name, {"_id": user["_id"]},
                                                  {"$set": {"pay_password": get_md5(new_password),
                                                            "has_pay_password": 1}})
            # 刷新缓存
            UserService.delete_cache(user["_id"])
        else:
            res['code'] = 10005
            res['message'] = '用户不存在'
        self.write(res)


class RefreshLoginHandler(BaseHandler):
    """
        刷新登录令牌（延长过期时间）
        get -> /refreshLogin/
    """

    @authenticated_async(None)
    async def get(self):
        channel = self.request.headers.get('Channel', 'default')
        res = res_func({})
        user = self.current_user
        payload = {
            'id': user["_id"],
            'username': user["username"],
            'exp': datetime.utcnow()
        }
        token = jwt.encode(payload=payload, key=self.settings["secret_key"], algorithm='HS256')
        res['data'] = {"token": token}
        # 存储用户令牌
        UserService.save_login_token(user["_id"], channel, token)
        self.write(res)
