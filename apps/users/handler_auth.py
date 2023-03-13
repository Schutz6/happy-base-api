import json
import jwt

from datetime import datetime
from apps.users.forms import LoginForm, UserForm, ChangePwdForm
from apps.users.models import User
from apps.users.service import UserService
from bases import utils
from bases.decorators import authenticated_async, log_async
from bases.handler import BaseHandler
from bases.res import resFunc
from bases.settings import settings
from bases.utils import get_md5, now


# 用户登录
class LoginHandler(BaseHandler):
    '''
        post -> /login/
        payload:
            {
                "username": "用户名",
                "password": "密码"
            }
    '''

    @log_async
    async def post(self):
        channel = self.request.headers.get('Channel', 'default')
        res = resFunc({})
        res['data'] = {"token": ""}
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = LoginForm.from_json(data)
        username = form.username.data
        password = form.password.data
        # 查找账号是否存在
        user_db = User()
        user = await user_db.find_one({"$or": [{"username": username}, {"email": username}, {"mobile": username}]})
        if user is not None:
            # 判断密码错误次数
            login_error_count = UserService.get_login_error_count(user["_id"])
            if login_error_count >= 5:
                res['code'] = 100061
                res['message'] = '账号已锁定'
                self.write(json.dumps(res, default=utils.json_serial))
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
                if user['status'] == 1:
                    payload = {
                        'id': user['_id'],
                        'username': user['username'],
                        'exp': datetime.utcnow()
                    }
                    token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
                    res['data'] = {"token": token.decode('utf-8')}
                    # 存储用户令牌
                    UserService.save_login_token(user["_id"], channel, token.decode('utf-8'))
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
        self.write(json.dumps(res, default=utils.json_serial))


# 用户信息
class UserHandler(BaseHandler):
    '''
        读取用户资料
        get -> /user/
    '''

    @authenticated_async
    async def get(self):
        res = resFunc({})
        current_user = self.current_user
        current_user["id"] = current_user["_id"]
        current_user["avatar"] = settings['SITE_URL'] + current_user["avatar"]
        res['data'] = current_user

        # 更新登录信息
        user_db = User()
        await user_db.update_one({"_id": current_user["_id"]}, {
            "$set": {"last_time": now(), "last_ip": self.request.remote_ip}})
        self.write(json.dumps(res, default=utils.json_serial))

    '''
        部分更新用户资料
        post -> /user/
        payload:
            {
                "name": "昵称",
                "gender": "性别",
                "introduction": "个人简介",
                "birthday": "生日",
                "avatar": "头像",
                "address": "地址"
            }

    '''

    @authenticated_async
    async def post(self):
        res = resFunc({})
        user = self.current_user
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = UserForm.from_json(data)
        user_db = User()
        if form.gender.data:
            gender = form.gender.data
            await user_db.update_one({"_id": user["_id"]}, {"$set": {"gender": gender}})
        if form.introduction.data:
            introduction = form.introduction.data
            await user_db.update_one({"_id": user["_id"]}, {"$set": {"introduction": introduction}})
        if form.birthday.data:
            birthday = form.birthday.data
            await user_db.update_one({"_id": user["_id"]}, {"$set": {"birthday": birthday}})
        if form.address.data:
            address = form.address.data
            await user_db.update_one({"_id": user["_id"]}, {"$set": {"address": address}})
        if form.name.data:
            name = form.name.data
            await user_db.update_one({"_id": user["_id"]}, {"$set": {"name": name}})
        if form.avatar.data:
            avatar = form.avatar.data
            # 替换地址
            avatar = avatar.replace(settings['SITE_URL'], "")
            await user_db.update_one({"_id": user["_id"]}, {"$set": {"avatar": avatar}})

        # 删除缓存
        UserService.delete_cache(user["_id"])

        self.write(res)


# 退出登录
class LogoutHandler(BaseHandler):
    '''
        get -> /logout/
    '''

    @authenticated_async
    async def get(self):
        res = resFunc({})
        channel = self.request.headers.get('Channel', 'default')
        current_user = self.current_user
        if current_user is not None:
            UserService.remove_login_token(current_user["_id"], channel)
        res["message"] = "成功退出"
        self.write(res)


# 修改用户密码
class ChangePwdHandler(BaseHandler):
    '''
    post -> /changePwd/
    payload:
        {
            "oldPassword": "旧密码"
            "newPassword": "新密码"
        }
    '''

    @authenticated_async
    async def post(self):
        res = resFunc({})
        user = self.current_user
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = ChangePwdForm.from_json(data)
        old_password = form.oldPassword.data
        new_password = form.newPassword.data
        if form.validate():
            user_db = User()
            user = user_db.find_one({"_id": user["_id"]})
            if user is not None:
                # 判断是否第一次修改密码
                if user["has_password"] == 1:
                    if user["password"] != get_md5(old_password):
                        res['code'] = 10006
                        res['message'] = '密码错误'
                    else:
                        await user_db.update_one({"_id": user["_id"]}, {"$set": {"password": get_md5(new_password)}})
                else:
                    await user_db.update_one({"_id": user["_id"]},
                                             {"$set": {"password": get_md5(new_password), "has_password": 1}})
                    # 刷新缓存
                    UserService.delete_cache(user["_id"])
            else:
                res['code'] = 10005
                res['message'] = '用户不存在'
        else:
            res['code'] = 50000
            res['message'] = "参数验证失败"
        self.write(res)


# 刷新登录令牌（延长过期时间）
class RefreshLoginHandler(BaseHandler):
    '''
       get -> /refreshLogin/
    '''

    @authenticated_async
    async def get(self):
        channel = self.request.headers.get('Channel', 'default')
        res = resFunc({})
        user = self.current_user
        payload = {
            'id': user["_id"],
            'username': user["username"],
            'exp': datetime.utcnow()
        }
        token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
        res['data'] = {"token": token.decode('utf-8')}
        # 存储用户令牌
        UserService.save_login_token(user["_id"], channel, token.decode('utf-8'))
        self.write(json.dumps(res, default=utils.json_serial))
