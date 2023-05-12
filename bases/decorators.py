import json
import time
import jwt

from apps.logs.models import Log
from apps.users.service import UserService
from bases.res import res_func
from bases.config import settings
from bases.utils import mongo_helper, show_error_log


# 管理员用户认证，日志记录
def authenticated_async(roles):
    def authenticated(func):

        async def wrapper(self):
            res = res_func({})
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
                        jwt=authorization,
                        key=settings['secret_key'],
                        leeway=jwt_expire,
                        algorithms=['HS256'],
                        options={"verify_exp": True}
                    )
                    user_id = data['id']
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
                except jwt.exceptions.PyJWTError as e:
                    show_error_log(e)
                    res['code'] = 10010
                    res['message'] = "令牌已失效"
                    self.write(res)
            else:
                res['code'] = 10010
                res['message'] = "令牌已失效"
                self.write(res)

        return wrapper
    return authenticated


# 日志记录
def log_async(func):
    async def wrapper(self):
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
    await mongo_helper.insert_one(Log.collection_name, await Log.get_json(
        {"username": username, "method": request.method, "uri": request.path, "params": params,
         "ip": request.remote_ip, "times": times}))
