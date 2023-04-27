import json
import time

import jwt

from functools import wraps
from threading import Thread
from apps.logs.models import Log
from apps.users.service import UserService
from bases.res import resFunc
from bases.settings import settings


# 管理员用户认证，日志记录
def authenticated_admin_async(func):

    async def wrapper(self):
        res = resFunc({})
        authorization = self.request.headers.get('Authorization', None)
        channel = self.request.headers.get('Channel', 'default')
        self.set_status(200)
        try:
            if authorization:
                authorization = authorization.split(' ')
                if len(authorization) != 2:
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.write(res)
                    return None
                else:
                    if authorization[0] != 'JWT':
                        res['code'] = 10010
                        res['message'] = "令牌已失效"
                        self.write(res)
                        return None
            else:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.write(res)
                return None
        except jwt.exceptions.PyJWTError:
            res['code'] = 10010
            res['message'] = "令牌已失效"
            self.write(res)
            return None

        authorization = authorization[1]

        if authorization:
            try:
                jwt_expire = settings['app_jwt_expire']
                if channel == "web_admin":
                    # 如果是后台管理
                    jwt_expire = settings['admin_jwt_expire']
                data = jwt.decode(
                    authorization,
                    settings['secret_key'],
                    leeway=jwt_expire,
                    options={"verify_exp": True}
                )
                user_id = data['id']
                # 判断令牌是否存在
                token = UserService.get_login_token(user_id, channel)
                if token is None or token == authorization:
                    # 获取用户信息
                    user = UserService.get_user_by_id(user_id)
                    self._current_user = user
                    # 判断是否管理员
                    if 'admin' in user["roles"] or 'superadmin' in user["roles"]:
                        # 开始时间
                        start_time = round(time.time()*1000, 2)
                        await func(self)
                        # 结束时间
                        finish_time = round(time.time()*1000, 2)
                        # 访问时间
                        times = round(finish_time - start_time, 2)
                        # 处理日志
                        do_log(self.request, user["username"], times)
                    else:
                        res['code'] = 10012
                        res['message'] = "权限不足"
                        self.write(res)
                else:
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.write(res)
            except jwt.exceptions.PyJWTError:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.write(res)
        else:
            res['code'] = 10010
            res['message'] = "令牌已失效"
            self.write(res)

    return wrapper


# 用户认证，日志记录
def authenticated_async(func):

    async def wrapper(self):
        res = resFunc({})
        authorization = self.request.headers.get('Authorization', None)
        channel = self.request.headers.get('Channel', 'default')
        self.set_status(200)
        try:
            if authorization:
                authorization = authorization.split(' ')
                if len(authorization) != 2:
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.write(res)
                    return None
                else:
                    if authorization[0] != 'JWT':
                        res['code'] = 10010
                        res['message'] = "令牌已失效"
                        self.write(res)
                        return None
            else:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.write(res)
                return None
        except jwt.exceptions.PyJWTError:
            res['code'] = 10010
            res['message'] = "令牌已失效"
            self.write(res)
            return None

        authorization = authorization[1]

        if authorization:
            try:
                jwt_expire = settings['app_jwt_expire']
                if channel == "web_admin":
                    # 如果是后台管理
                    jwt_expire = settings['admin_jwt_expire']
                data = jwt.decode(
                    authorization,
                    settings['secret_key'],
                    leeway=jwt_expire,
                    options={"verify_exp": True}
                )
                user_id = data['id']
                # 判断令牌是否存在
                token = UserService.get_login_token(user_id, channel)
                if token is None or token == authorization:
                    # 获取用户信息
                    user = UserService.get_user_by_id(user_id)
                    self._current_user = user
                    # 开始时间
                    start_time = round(time.time()*1000, 2)
                    await func(self)
                    # 结束时间
                    finish_time = round(time.time()*1000, 2)
                    # 访问时间
                    times = round(finish_time - start_time, 2)
                    # 处理日志
                    do_log(self.request, user["username"], times)
                else:
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.write(res)
            except jwt.exceptions.PyJWTError:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.write(res)
        else:
            res['code'] = 10010
            res['message'] = "令牌已失效"
            self.write(res)

    return wrapper


def owner_required(func):

    @wraps(func)
    async def wrapper(self):
        await func(self)

    return wrapper


# 日志记录
def log_async(func):

    async def wrapper(self):
        # 开始时间
        start_time = round(time.time()*1000, 2)
        await func(self)
        # 结束时间
        finish_time = round(time.time()*1000, 2)
        # 访问时间
        times = round(finish_time - start_time, 2)
        # 处理日志
        do_log(self.request, "", times)

    return wrapper


# 异步执行方法
def run_async(func):

    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


# 处理日志
@run_async
def do_log(request, username, times):
    # 接口参数
    params = ""
    # 过滤文件上传接口，规则：/file/upload/ 开头
    if request.uri.find("/file/upload/") == -1:
        if request.method.upper() == "POST":
            params = str(request.body, encoding="utf-8")
        elif request.method.upper() == "GET":
            params = request.query
    # 记录日志
    add_log(username, request.method, request.path, params, request.remote_ip, times)


# 异步执行添加日志
def add_log(username, method, uri, params, ip, times):
    if uri == "/login/":
        params = json.loads(params)
        params["password"] = "***"
        params = json.dumps(params)
    log_db = Log()
    log_db.username = username
    log_db.method = method
    log_db.uri = uri
    log_db.params = params
    log_db.ip = ip
    log_db.times = times
    log_db.insert_one(log_db.get_add_json())
