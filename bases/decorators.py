import time

import jwt

from functools import wraps
from threading import Thread
from apps.logs.models import Log
from apps.users.service import UserService
from bases.res import resFunc
from bases.settings import settings


# 用户认证，日志记录
def authenticated_async(func):

    async def wrapper(self, *args, **kwargs):
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
                    self.finish(res)
                    return None
                else:
                    if authorization[0] != 'JWT':
                        res['code'] = 10010
                        res['message'] = "令牌已失效"
                        self.finish(res)
                        return None
            else:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.finish(res)
                return None
        except jwt.exceptions.PyJWTError:
            res['code'] = 10010
            res['message'] = "令牌已失效"
            self.finish(res)

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
                    user = await UserService.get_user_by_id(user_id)
                    self._current_user = user
                    # 开始时间
                    start_time = round(time.time()*1000, 2)
                    await func(self, *args, **kwargs)
                    # 结束时间
                    finish_time = round(time.time()*1000, 2)
                    # 访问时间
                    times = round(finish_time - start_time, 2)
                    # 记录日志
                    await add_log(user['username'], self.request.method, self.request.uri,
                                  str(self.request.body, encoding="utf-8"),
                                  self.request.remote_ip, times)
                else:
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.finish(res)
            except jwt.exceptions.PyJWTError:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.finish(res)
        else:
            res['code'] = 10010
            res['message'] = "令牌已失效"
            self.finish(res)

    return wrapper


def owner_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        await func(self, *args, **kwargs)

    return wrapper


# 日志记录
def log_async(func):
    async def wrapper(self, *args, **kwargs):
        # 开始时间
        start_time = round(time.time()*1000, 2)
        await func(self, *args, **kwargs)
        # 结束时间
        finish_time = round(time.time()*1000, 2)
        # 访问时间
        times = round(finish_time - start_time, 2)
        # 记录日志
        await add_log("", self.request.method, self.request.uri,
                      str(self.request.body, encoding="utf-8"),
                      self.request.remote_ip, times)
    return wrapper


# 异步执行方法
def run_async(func):
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


# 异步执行添加日志
async def add_log(username, method, uri, params, ip, times):
    log_db = Log()
    log_db.username = username
    log_db.method = method
    log_db.uri = uri
    log_db.params = params
    log_db.ip = ip
    log_db.times = times
    await log_db.insert_one(log_db.get_add_json())
