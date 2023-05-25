import json
import time
import jwt

from core.blacklist.service import BlacklistService
from core.cores.service import CoreService
from core.logs.models import Log
from core.params.service import ParamService
from core.users.service import UserService
from base.res import res_func
from config import settings
from base.utils import mongo_helper, now_utc


def authenticated_core(func):
    """ 核心认证，日志记录 """

    async def wrapper(self):
        res = res_func({})
        authorization = self.request.headers.get('Authorization', None)
        channel = self.request.headers.get('Channel', 'default')
        mid = self.request.headers.get('Mid', None)

        # 判断是否IP限流
        if await handle_ip_limit(self.request.remote_ip):
            pass
        else:
            res['code'] = 10011
            res['message'] = "操作太频繁"
            self.write(res)
            return None

        # 获取模块信息
        if mid is not None:
            # 获取模块信息
            module = await CoreService.get_module(mid)
            if module is not None:
                roles = []
                # 判断接口是否具有权限
                api = self.request.uri
                for item in module["api_json"]:
                    if api.find(item["id"]) > -1:
                        roles = item["roles"]
                        # 判断接口是否启用
                        if item["status"]:
                            break
                        else:
                            res['code'] = 50000
                            res['message'] = "接口没激活"
                            self.write(res)
                            return None
                if len(roles) > 0:
                    if authorization is not None:
                        authorization = authorization.split(' ')
                        if len(authorization) != 2 and authorization[0] != 'JWT':
                            res['code'] = 10010
                            res['message'] = "令牌已失效"
                            self.write(res)
                        else:
                            try:
                                authorization = authorization[1]

                                jwt_expire = settings['app_jwt_expire']
                                if channel == "web_admin":
                                    # 如果是后台管理
                                    jwt_expire = settings['admin_jwt_expire']
                                data = jwt.decode(
                                    jwt=authorization,
                                    key=settings['secret_key'],
                                    leeway=jwt_expire,
                                    algorithms=['HS256'],
                                    options={"verify_exp": True}
                                )
                                user_id = data.get('id')
                                # 判断令牌是否存在
                                token = UserService.get_login_token(user_id, channel)
                                if token is None or token == authorization:
                                    # 获取用户信息
                                    user = await UserService.get_user_by_id(user_id)
                                    user["module"] = module
                                    self._current_user = user
                                    # 判断是否有权限
                                    flag = False
                                    for role in user["roles"]:
                                        if role in roles:
                                            flag = True
                                            break
                                    if flag:
                                        # 开始时间
                                        start_time = round(time.time() * 1000, 2)
                                        await func(self)
                                        # 结束时间
                                        finish_time = round(time.time() * 1000, 2)
                                        # 访问时间
                                        times = round(finish_time - start_time, 2)
                                        # 处理日志
                                        await handle_log(self.request, user["username"], times)
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
                else:
                    # 初始化模块
                    self._current_user = {"module": module}
                    # 开始时间
                    start_time = round(time.time() * 1000, 2)
                    await func(self)
                    # 结束时间
                    finish_time = round(time.time() * 1000, 2)
                    # 访问时间
                    times = round(finish_time - start_time, 2)
                    # 处理日志
                    await handle_log(self.request, "", times)
            else:
                res['code'] = 50000
                res['message'] = "错误调用"
                self.write(res)
        else:
            res['code'] = 50000
            res['message'] = "错误调用"
            self.write(res)
    return wrapper


def authenticated_async(roles):
    """ 管理员用户认证，日志记录 """

    def authenticated(func):

        async def wrapper(self):
            res = res_func({})
            authorization = self.request.headers.get('Authorization', None)
            channel = self.request.headers.get('Channel', 'default')
            if authorization is not None:
                authorization = authorization.split(' ')
                if len(authorization) != 2 and authorization[0] != 'JWT':
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.write(res)
                    return None
            else:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.write(res)
                return None

            authorization = authorization[1]

            try:
                # 判断是否IP限流
                if await handle_ip_limit(self.request.remote_ip):
                    pass
                else:
                    res['code'] = 10011
                    res['message'] = "操作太频繁"
                    self.write(res)
                    return None

                jwt_expire = settings['app_jwt_expire']
                if channel == "web_admin":
                    # 如果是后台管理
                    jwt_expire = settings['admin_jwt_expire']
                data = jwt.decode(
                    jwt=authorization,
                    key=settings['secret_key'],
                    leeway=jwt_expire,
                    algorithms=['HS256'],
                    options={"verify_exp": True}
                )
                user_id = data.get("id")
                # 判断令牌是否存在
                token = UserService.get_login_token(user_id, channel)
                if token is None or token == authorization:
                    # 获取用户信息
                    user = await UserService.get_user_by_id(user_id)
                    self._current_user = user
                    if roles is not None:
                        # 判断是否有权限
                        flag = False
                        for role in user["roles"]:
                            if role in roles:
                                flag = True
                                break
                        if flag:
                            # 开始时间
                            start_time = round(time.time() * 1000, 2)
                            await func(self)
                            # 结束时间
                            finish_time = round(time.time() * 1000, 2)
                            # 访问时间
                            times = round(finish_time - start_time, 2)
                            # 处理日志
                            await handle_log(self.request, user["username"], times)
                        else:
                            res['code'] = 10012
                            res['message'] = "权限不足"
                            self.write(res)
                    else:
                        # 开始时间
                        start_time = round(time.time() * 1000, 2)
                        await func(self)
                        # 结束时间
                        finish_time = round(time.time() * 1000, 2)
                        # 访问时间
                        times = round(finish_time - start_time, 2)
                        # 处理日志
                        await handle_log(self.request, user["username"], times)
                else:
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.write(res)
            except jwt.exceptions.PyJWTError:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.write(res)

        return wrapper

    return authenticated


# 日志记录
def log_async(func):
    async def wrapper(self):
        # 判断是否IP限流
        if await handle_ip_limit(self.request.remote_ip):
            pass
        else:
            res = res_func({})
            res['code'] = 10011
            res['message'] = "操作太频繁"
            self.write(res)
            return None
        # 开始时间
        start_time = round(time.time() * 1000, 2)
        await func(self)
        # 结束时间
        finish_time = round(time.time() * 1000, 2)
        # 访问时间
        times = round(finish_time - start_time, 2)
        # 处理日志
        await handle_log(self.request, "", times)

    return wrapper


# 处理IP限流
async def handle_ip_limit(ip):
    # 接口限流次数
    api_limit = 200
    param = await ParamService.get_param("apiLimit")
    if param is not None:
        api_limit = int(param["value"])
    # 获取接口访问次数
    api_limit_num = BlacklistService.get_api_limit()
    if api_limit_num >= api_limit:
        return False

    # 判断IP是否在黑名单
    if await BlacklistService.has_ip_blacklist(ip):
        # 在黑名单，禁止访问
        return False
    else:
        # 单IP限制次数
        ip_limit = 20
        param = await ParamService.get_param("ipLimit")
        if param is not None:
            ip_limit = int(param["value"])
        # 获取IP访问次数
        ip_limit_num = BlacklistService.get_ip_limit(ip)
        if ip_limit_num >= ip_limit:
            # 加入到黑名单
            await BlacklistService.add_ip_blacklist(ip)
            return False
    return True


# 处理日志
async def handle_log(request, username, times):
    # 接口参数
    params = ""
    # 过滤文件上传接口，规则：/file/upload/ 开头
    if request.uri.find("/file/upload/") == -1:
        if request.method.upper() == "POST":
            params = str(request.body, encoding="utf-8")
        elif request.method.upper() == "GET":
            params = request.query
    if request.path == "/login/":
        params = json.loads(params)
        params["password"] = "***"
        params = json.dumps(params)
    # 记录日志
    await mongo_helper.insert_one(Log.collection_name,
                                  {"username": username, "method": request.method, "uri": request.path,
                                   "params": params, "ip": request.remote_ip, "times": times, "add_time": now_utc()})
