import json

from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func, res_fail_func
from base.utils import mongo_helper
from core.users.models import User
from core.users.service import UserService
from ext.user.func import lock_user_recharge_or_withdraw


class BindInviteCodeHandler(BaseHandler):
    """
        绑定邀请码
        post -> /user/bindInviteCode/
        payload:
          {
              "invite_code": "邀请码"
          }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_fail_func(None)
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        invite_code = req_data.get("invite_code")

        if invite_code is not None:
            current_user = self.current_user
            invite_code = int(invite_code)
            if current_user["_id"] != invite_code:
                # 查询邀请码是否存在
                invite_user = await UserService.get_user_by_id(invite_code)
                if invite_user is not None:
                    # 绑定上级用户
                    await mongo_helper.update_one(User.collection_name, {"_id": current_user["_id"]},
                                                  {"$set": {"pid": invite_user["_id"]}})
                    # 删除缓存
                    UserService.delete_cache(current_user["_id"])
                    res = res_func({})
        self.write(res)


class RealnameHandler(BaseHandler):
    """
        实名认证
        post -> /user/realname/
        {
            "full_name": "姓名",
            "id_number": "身份证号"
        }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        full_name = req_data.get("full_name")
        id_number = req_data.get("id_number")

        current_user = self.current_user
        await mongo_helper.update_one(User.collection_name, {"_id": current_user["_id"]},
                                      {"$set": {"full_name": full_name, "id_number": id_number, "certified": 2}})
        # 删除缓存
        UserService.delete_cache(current_user["_id"])
        self.write(res)


class CertifiedHandler(BaseHandler):
    """
        审核用户
        post -> /user/certified/
        {
            "id": "用户编号",
            "certified": "审核状态"
        }
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _id = req_data.get("id")
        certified = req_data.get("certified")

        await mongo_helper.update_one(User.collection_name, {"_id": _id}, {"$set": {"certified": certified}})
        # 删除缓存
        UserService.delete_cache(_id)
        self.write(res)


class UserBalanceHandler(BaseHandler):
    """
        后台充值/提现
        post -> /user/balance/
        {
            "id": "用户编号",
            "money": "金额"
        }
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_fail_func(None)
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _id = req_data.get("id")
        money = req_data.get("money")
        if _id is not None and money is not None:
            _id = int(_id)
            money = float(money)
            # 处理充值提现
            res = await lock_user_recharge_or_withdraw("3", _id, money)
        self.write(res)
