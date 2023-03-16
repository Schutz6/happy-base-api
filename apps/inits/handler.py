import json

from apps.roles.models import Role
from apps.users.models import User
from bases.decorators import log_async
from bases.handler import BaseHandler
from bases.res import resFunc
from bases.utils import get_md5, get_random_head


# 初始化基础数据（谨慎操作）
class InitDataHandler(BaseHandler):
    '''
       get -> /init/data/
    '''

    @log_async
    async def get(self):
        res = resFunc({})
        # 判断是否需要初始化用户数据
        user_db = User()
        user = await user_db.find_one({"username": "superadmin"})
        if user is None:
            user_db.name = "超级管理员"
            user_db.username = "superadmin"
            user_db.gender = "no"
            user_db.password = get_md5("123456")
            user_db.has_password = 1
            user_db.status = 1
            user_db.avatar = get_random_head()
            user_db.roles = ["superadmin"]
            await user_db.insert_one(user_db.get_add_json())

            user_db1 = User()
            user_db1.name = "管理员"
            user_db1.username = "admin"
            user_db1.gender = "no"
            user_db1.password = get_md5("123456")
            user_db1.has_password = 1
            user_db1.status = 1
            user_db1.avatar = get_random_head()
            user_db1.roles = ["superadmin"]
            await user_db1.insert_one(user_db1.get_add_json())

            # 新增角色
            role_db1 = Role()
            role_db1.name = "superadmin"
            role_db1.describe = "超级管理员"
            await role_db1.insert_one(role_db1.get_add_json())

            role_db2 = Role()
            role_db2.name = "user"
            role_db2.describe = "普通用户"
            await role_db2.insert_one(role_db2.get_add_json())

            role_db3 = Role()
            role_db3.name = "admin"
            role_db3.describe = "普通管理员"
            await role_db3.insert_one(role_db3.get_add_json())

        self.write(json.dumps(res))
