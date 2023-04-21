import json

from apps.menus.models import Menu
from apps.params.models import Param
from apps.roles.models import Role
from apps.users.models import User
from bases.decorators import log_async
from bases.handler import BaseHandler
from bases.res import resFunc
from bases.utils import get_md5, get_random_head


class InitDataHandler(BaseHandler):
    '''
        初始化基础数据（谨慎操作）
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
            user_db.email = "superadmin@admin.com"
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
            user_db1.email = "admin@admin.com"
            user_db1.gender = "no"
            user_db1.password = get_md5("123456")
            user_db1.has_password = 1
            user_db1.status = 1
            user_db1.avatar = get_random_head()
            user_db1.roles = ["admin"]
            await user_db1.insert_one(user_db1.get_add_json())

            # 新增角色
            role_db1 = Role()
            role_db1.name = "superadmin"
            role_db1.describe = "超级管理员"
            role_db1.remarks = "拥有所有权限（不要删）"
            role_db1.sort = 99
            await role_db1.insert_one(role_db1.get_add_json())

            role_db2 = Role()
            role_db2.name = "user"
            role_db2.describe = "普通用户"
            role_db2.remarks = "没后台权限（不要删）"
            role_db2.sort = 97
            await role_db2.insert_one(role_db2.get_add_json())

            role_db3 = Role()
            role_db3.name = "admin"
            role_db3.describe = "普通管理员"
            role_db3.remarks = "拥有部分权限（不要删）"
            role_db3.sort = 98
            await role_db3.insert_one(role_db3.get_add_json())

            # 新增菜单
            menu_db = Menu()
            menu_db.pid = 0
            menu_db.name = "首页概况"
            menu_db.url = "/pages/index/index"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 1
            menu_db.sort = 900
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 0
            menu_db.name = "系统管理"
            menu_db.url = "#"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 1
            menu_db.sort = 100
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "用户管理"
            menu_db.url = "/pages/system/user/user"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 2
            menu_db.sort = 190
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "角色管理"
            menu_db.url = "/pages/system/role/role"
            menu_db.roles = ["superadmin"]
            menu_db.level = 2
            menu_db.sort = 180
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "菜单管理"
            menu_db.url = "/pages/system/menus/menus"
            menu_db.roles = ["superadmin"]
            menu_db.level = 2
            menu_db.sort = 170
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "字典管理"
            menu_db.url = "/pages/system/dict/dict"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 2
            menu_db.sort = 160
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "参数管理"
            menu_db.url = "/pages/system/param/param"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 2
            menu_db.sort = 150
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "任务管理"
            menu_db.url = "/pages/system/task/task"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 2
            menu_db.sort = 140
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "文件管理"
            menu_db.url = "/pages/system/files/files"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 2
            menu_db.sort = 130
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            menu_db = Menu()
            menu_db.pid = 1
            menu_db.name = "系统日志"
            menu_db.url = "/pages/system/logs/logs"
            menu_db.roles = ["superadmin", "admin"]
            menu_db.level = 2
            menu_db.sort = 120
            menu_db.status = 1
            await menu_db.insert_one(menu_db.get_add_json())

            param_db = Param()
            param_db.key = "siteName"
            param_db.value = "网站名称"
            param_db.status = 0
            param_db.remarks = "网站名称"
            await param_db.insert_one(param_db.get_add_json())

        self.write(res)
