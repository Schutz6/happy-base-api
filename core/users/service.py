import json

from core.users.models import User
from config import settings
from base.keys import Keys
from base.utils import get_random_num, redis_helper, mongo_helper


class UserService(object):
    """用户服务类"""

    # 存储登录令牌
    @staticmethod
    def save_login_token(_id, channel, token):
        if channel == 'web_admin':
            redis_helper.redis.set(Keys.tokenKey + str(_id) + ":" + channel, token,
                                   ex=settings["admin_jwt_expire"])
        else:
            redis_helper.redis.set(Keys.tokenKey + str(_id) + ":" + channel, token, ex=settings["app_jwt_expire"])

    # 删除登录令牌
    @staticmethod
    def remove_login_token(_id, channel):
        redis_helper.redis.delete(Keys.tokenKey + str(_id) + ":" + channel)

    # 获取登录令牌
    @staticmethod
    def get_login_token(_id, channel):
        return redis_helper.redis.get(Keys.tokenKey + str(_id) + ":" + channel)

    # 记录登录错误次数
    @staticmethod
    def add_login_error_count(_id):
        login_error_count = redis_helper.redis.get(Keys.loginErrorKey + str(_id))
        if login_error_count is not None:
            redis_helper.redis.set(Keys.loginErrorKey + str(_id), int(login_error_count) + 1, ex=300)
        else:
            redis_helper.redis.set(Keys.loginErrorKey + str(_id), 1, ex=300)

    # 获取登录密码错误次数
    @staticmethod
    def get_login_error_count(_id):
        login_error_count = redis_helper.redis.get(Keys.loginErrorKey + str(_id))
        if login_error_count is None:
            return 0
        else:
            return int(login_error_count)

    # 删除登录次数
    @staticmethod
    def delete_login_error_cache(_id):
        redis_helper.redis.delete(Keys.loginErrorKey + str(_id))

    # 根据id获取用户对象
    @staticmethod
    async def get_user_by_id(_id):
        # 获取缓存
        user = redis_helper.redis.get(Keys.userKey + str(_id))
        if user is None:
            user = await mongo_helper.fetch_one(User.collection_name, {"_id": int(_id)})
            if user is not None:
                # 清空密码
                user["id"] = user["_id"]
                user['password'] = ''
                user['pay_password'] = ''
                redis_helper.redis.set(Keys.userKey + str(_id), json.dumps(user))
        else:
            user = json.loads(user)
        return user

    # 删除缓存
    @staticmethod
    def delete_cache(_id):
        redis_helper.redis.delete(Keys.userKey + str(_id))

    # 生成一个账号
    @staticmethod
    async def get_account_number():
        username = get_random_num(6)
        # 判断是否已存在
        user = await mongo_helper.fetch_one(User.collection_name, {"username": username})
        if user is not None:
            username = await UserService.get_account_number()
        return username
