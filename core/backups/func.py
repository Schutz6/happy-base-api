from core.menus.models import Menu
from core.params.models import Param
from core.roles.models import Role
from core.tasks.models import Task
from core.users.models import User
from base.utils import mongo_helper, get_md5, get_random_head


async def init_db_data():
    """初始化数据库"""
    num = await mongo_helper.fetch_count_info(User.collection_name, {})
    if num == 0:
        # 初始化用户
        await init_user()
        # 初始化角色
        await init_role()
        # 初始化菜单
        await init_menu()
        # 初始化参数
        await init_param()
        # 初始化任务
        await init_task()


async def init_user():
    """初始化用户编号"""
    await mongo_helper.insert_one(User.collection_name, {"_id": "sequence_id", "seq": 100000 - 1})
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
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "模块管理", "icon": "/icons/icon-code.png",
                                   "url": "/pages/system/code/code", "roles": ["super"], "level": 2,
                                   "sort": 100,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "备份管理", "icon": "/icons/icon-db.png",
                                   "url": "/pages/system/backup/backup", "roles": ["super"], "level": 2,
                                   "sort": 90,
                                   "status": 1})
    pid = await mongo_helper.insert_one(Menu.collection_name,
                                        {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": 0,
                                         "name": "会员管理", "icon": "/icons/icon-list.png",
                                         "url": "#", "roles": ["super", 'admin'], "level": 1, "sort": 300, "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "会员列表", "icon": "/icons/icon-member.png",
                                   "url": "/pages/ext/member/member", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 390,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "会员认证", "icon": "/icons/icon-realname.png",
                                   "url": "/pages/ext/member/realname", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 380,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "提现卡管理", "icon": "/icons/icon-item.png",
                                   "url": "/pages/core/list?mid=Bankcard", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 370,
                                   "status": 1})
    pid = await mongo_helper.insert_one(Menu.collection_name,
                                        {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": 0,
                                         "name": "财务管理", "icon": "/icons/icon-list.png",
                                         "url": "#", "roles": ["super", 'admin'], "level": 1, "sort": 200, "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "充值记录", "icon": "/icons/icon-item.png",
                                   "url": "/pages/ext/recharge/recharge", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 290,
                                   "status": 1})
    await mongo_helper.insert_one(Menu.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Menu.collection_name), "pid": pid,
                                   "name": "提现记录", "icon": "/icons/icon-item.png",
                                   "url": "/pages/ext/withdraw/withdraw", "roles": ["super", 'admin'], "level": 2,
                                   "sort": 280,
                                   "status": 1})


async def init_param():
    """初始化参数"""
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "siteName",
                                   "value": "低代码基础平台", "status": 0, "remarks": "管理后台名称"})
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "appName",
                                   "value": "低代码APP", "status": 0, "remarks": "APP名称"})
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "ipLimit",
                                   "value": "100", "status": 1, "remarks": "每秒单IP访问限流次数，超过次数加入IP黑名单"})
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "apiLimit",
                                   "value": "20000", "status": 1, "remarks": "接口限流，每秒20000次"})
    await mongo_helper.insert_one(Param.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Param.collection_name), "key": "ipWhiteList",
                                   "value": "127.0.0.1", "status": 1, "remarks": "IP白名单"})


async def init_task():
    """初始化任务"""
    await mongo_helper.insert_one(Task.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Task.collection_name),
                                   "name": "清理日志-保留7天日志",
                                   "func": "core.logs.tasks:clear_log", "type": 2, "exec_cron": "1:00D", "status": 0,
                                   "options": "7"})
    await mongo_helper.insert_one(Task.collection_name,
                                  {"_id": await mongo_helper.get_next_id(Task.collection_name),
                                   "name": "测试任务",
                                   "func": "core.tasks.tasks:test", "type": 3, "exec_interval": "1S", "status": 0,
                                   "options": "测试中"})
