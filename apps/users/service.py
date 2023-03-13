import json

from apps.users.models import User
from bases import utils
from bases.service import BaseService
from bases.settings import settings
from bases.utils import get_random_num


# 用户服务类
class UserService(BaseService):

    # 存储登录令牌
    @staticmethod
    def save_login_token(_id, channel, token):
        if channel == 'web_admin':
            UserService.redis.set(UserService.tokenKey + str(_id) + ":" + channel, token,
                                  ex=settings["admin_jwt_expire"])
        else:
            UserService.redis.set(UserService.tokenKey + str(_id) + ":" + channel, token, ex=settings["app_jwt_expire"])

    # 删除登录令牌
    @staticmethod
    def remove_login_token(_id, channel):
        UserService.redis.delete(UserService.tokenKey + str(_id) + ":" + channel)

    # 获取登录令牌
    @staticmethod
    def get_login_token(_id, channel):
        return UserService.redis.get(UserService.tokenKey + str(_id) + ":" + channel)

    # 记录登录错误次数
    @staticmethod
    def add_login_error_count(_id):
        login_error_count = UserService.redis.get(UserService.loginErrorKey + str(_id))
        if login_error_count is not None:
            UserService.redis.set(UserService.loginErrorKey + str(_id), int(login_error_count) + 1, ex=1800)
        else:
            UserService.redis.set(UserService.loginErrorKey + str(_id), 1, ex=1800)

    # 获取登录密码错误次数
    @staticmethod
    def get_login_error_count(_id):
        login_error_count = UserService.redis.get(UserService.loginErrorKey + str(_id))
        if login_error_count is None:
            return 0
        else:
            return int(login_error_count)

    # 删除登录次数
    @staticmethod
    def delete_login_error_cache(_id):
        UserService.redis.delete(UserService.loginErrorKey + str(_id))

    # 根据id获取用户对象
    @staticmethod
    async def get_user_by_id(_id):
        # 获取缓存
        user = UserService.redis.get(UserService.userKey + str(_id))
        if user is None:
            user_db = User()
            user = await user_db.find_one({"_id": int(_id)})
            if user is not None:
                # 清空密码
                user["id"] = user["_id"]
                user['password'] = ''
                UserService.redis.set(UserService.userKey + str(_id), json.dumps(user, default=utils.json_serial))
        else:
            user = json.loads(user)
        return user

    # 删除缓存
    @staticmethod
    def delete_cache(_id):
        UserService.redis.delete(UserService.userKey + str(_id))

    # 生成一个账号
    @staticmethod
    async def get_account_number():
        username = get_random_num(6)

        # 判断是否已存在
        user_db = User()
        user = await user_db.find_one({"username": username})
        if user is not None:
            username = await UserService.get_account_number()
        return username
