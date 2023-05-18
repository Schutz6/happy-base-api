from apps.menus.models import Menu
from apps.params.models import Param
from apps.roles.models import Role
from apps.users.models import User
from bases.utils import mongo_helper, get_md5, get_random_head


async def init_db_data():
    """初始化数据库"""
    user = await mongo_helper.fetch_one(User.collection_name, {"username": {"$in": ["super", "admin"]}})
    if user is None:
        # 初始化用户
        await init_user()
        # 初始化角色
        await init_role()
        # 初始化菜单
        await init_menu()
        # 初始化参数
        await init_param()


async def init_user():
    """初始化用户编号"""
    await mongo_helper.insert_one(User.collection_name, {"_id": "sequence_id", "seq": 100000})
    """初始化用户"""
    await mongo_helper.insert_one(User.collection_name,
                                  {"_id": await mongo_helper.get_next_id(User.collection_name), "name": "超级管理员",
                                   "username": "super", "email": "super@admin.com", "gender": "no",
                                   "password": get_md5("123456"), "has_password": 1, "status": 1,
                                   "avatar": get_random_head(),
                                   "roles": ["super"]})
    await mongo_helper.insert_one(User.collection_name,
                                  {"_id": await mongo_helper.get_next_id(User.collection_name), "name": "管理员",
                                   "username": "admin", "email": "admin@admin.com", "gender": "no",
                                   "password": get_md5("123456"), "has_password": 1, "status": 1,
                                   "avatar": get_random_head(),
                                   "roles": ["admin"]})


async def init_role():
    """初始化角色"""
    await mongo_helper.insert_one(Role.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Role.collection_name), "name": "super",
                                   "describe": "超管", "remarks": "拥有所有权限（不要删）", "sort": 90})
    await mongo_helper.insert_one(Role.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Role.collection_name), "name": "admin",
                                   "describe": "普管", "remarks": "拥有部分权限（不要删）", "sort": 80})
    await mongo_helper.insert_one(Role.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Role.collection_name), "name": "user",
                                   "describe": "用户", "remarks": "没后台权限（不要删）", "sort": 70})


async def init_menu():
    """初始化菜单"""
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": 0,
                                   "name": "首页概况", "icon": "/icons/icon-overview.png",
                                   "url": "/pages/index/index", "roles": ["super", 'admin'], "level": 1, "sort": 900,
                                   "status": 1})
    pid = await mongo_helper.insert_one(Menu.collection_name,
                                        {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": 0,
                                         "name": "系统管理", "icon": "/icons/icon-system.png",
                                         "url": "#", "roles": ["super", 'admin'], "level": 1, "sort": 100, "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "用户管理", "icon": "/icons/icon-user.png",
                                   "url": "/pages/system/user/user", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 190,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "角色管理", "icon": "/icons/icon-role.png",
                                   "url": "/pages/system/role/role", "roles": ["super"], "level": 2, "sort": 180,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "菜单管理", "icon": "/icons/icon-menu.png",
                                   "url": "/pages/system/menus/menus", "roles": ["super"], "level": 2, "sort": 170,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "字典管理", "icon": "/icons/icon-dict.png",
                                   "url": "/pages/system/dict/dict", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 160,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "参数管理", "icon": "/icons/icon-param.png",
                                   "url": "/pages/system/param/param", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 150,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "任务管理", "icon": "/icons/icon-task.png",
                                   "url": "/pages/system/task/task", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 140,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "文件管理", "icon": "/icons/icon-file.png",
                                   "url": "/pages/system/files/files", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 130,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "系统日志", "icon": "/icons/icon-log.png",
                                   "url": "/pages/system/logs/logs", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 120,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "IP黑名单", "icon": "/icons/icon-blacklist.png",
                                   "url": "/pages/system/blacklist/blacklist", "roles": ["super"], "level": 2,
                                   "sort": 110,
                                   "status": 1})


async def init_param():
    """初始化参数"""
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "siteName",
                                   "value": "网站名称", "status": 0, "remarks": "网站名称"})
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "ipLimit",
                                   "value": "10", "status": 1, "remarks": "每秒单IP访问限流次数，超过次数加入IP黑名单"})
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "apiLimit",
                                   "value": "200", "status": 1, "remarks": "接口限流，每秒200次"})
