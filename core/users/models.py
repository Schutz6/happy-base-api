from base.utils import now_utc, mongo_helper


class User(object):
    """用户"""

    # 文档名
    collection_name = "User"

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

    # 上级用户
    pid = 0
    # 邮箱
    email = None
    # 区号
    area = None
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
    # 最后访问时间
    last_time = None
    # 最后访问IP
    last_ip = None

    # 积分
    integral = 0
    # 余额
    balance = 0

    # 支付密码
    pay_password = None
    # 是否设置支付密码 0未设置 1已设置
    has_pay_password = 0

    # 认证状态 0未认证 1已认证 2审核中 3认证失败
    certified = 0
    # 姓名
    full_name = None
    # 身份证号
    id_number = None

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(User.collection_name)
        return {"_id": _id,
                "name": req_data.get("name"),
                "username": req_data.get("username"),
                "password": req_data.get("password"),
                "has_password": req_data.get("has_password", 1),
                "status": req_data.get("status", 0),
                "roles": req_data.get("roles", []),
                "email": req_data.get("email"),
                "mobile": req_data.get("mobile"),
                "gender": req_data.get("gender"),
                "avatar": req_data.get("avatar"),
                "address": req_data.get("address"),
                "introduction": req_data.get("introduction"),
                "birthday": req_data.get("birthday"),
                "add_time": now_utc()}
