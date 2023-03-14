from bases.settings import settings
from bases.models import MongoModel
from bases.utils import now


# 用户对象
class User(MongoModel):

    def __init__(self):
        super(User, self).__init__(settings['mongo']['name'], "User")

    """"数据库字段声明"""
    # 昵称
    name = None
    # 账号
    username = None
    # 密码
    password = None
    # 是否设置密码 0未设置 1已设置
    has_password = 0
    # 状态 1正常 2注销
    status = 0,
    # 角色
    roles = []

    # 扩展字段

    # 邮箱
    email = None
    # 手机号
    mobile = None
    # 性别 男male 女female 未知no
    gender = None
    # 头像
    avatar = None
    # 地址
    address = None
    # 简介
    introduction = None
    # 生日
    birthday = None

    # 格式化json
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "name": self.name,
                "username": self.username,
                "password": self.password,
                "has_password": self.has_password,
                "status": self.status,
                "roles": self.roles,
                "email": self.email,
                "mobile": self.mobile,
                "gender": self.gender,
                "avatar": self.avatar,
                "address": self.address,
                "introduction": self.introduction,
                "birthday": self.birthday,
                "add_time": now()}
