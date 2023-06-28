import json

from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_fail_func, res_func
from base.utils import mongo_helper, get_md5, now_utc
from core.users.models import User
from ext.user.func import lock_update_user_balance, lock_user_withdraw


class UserWithdrawHandler(BaseHandler):
    """
        用户提现
        post -> /user/withdraw/
        payload:
            {
                "type": "卡类型",
                "name": "户名",
                "bank_name": "银行名称",
                "branch_name": "支行名称",
                "card_number": "银行卡号",
                "address_usdt": "USDT地址",
                "money": "提现金额",
                "pay_password": "支付密码"
            }
    """

    @authenticated_async(None)
    async def post(self, *args, **kwargs):
        res = res_fail_func(None, message="操作失败")
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _type = req_data.get("type")
        name = req_data.get("name")
        bank_name = req_data.get("bank_name")
        branch_name = req_data.get("branch_name")
        card_number = req_data.get("card_number")
        address_usdt = req_data.get("address_usdt")
        money = req_data.get("money")
        pay_password = req_data.get("pay_password")

        current_user = self.current_user

        # 判断支付密码是否正确
        user = await mongo_helper.fetch_one(User.collection_name, {"_id": current_user["_id"]})
        if user.get("pay_password") != get_md5(pay_password):
            res['code'] = 10006
            res['message'] = '支付密码错误'
        elif user.get("certified", 0) != 1:
            res['code'] = 11006
            res['message'] = '请先认证'
        else:
            money = abs(float(money))
            res = await lock_user_withdraw(current_user["_id"], money)
            if res["code"] == 20000:
                # 添加提现记录
                withdraw_id = await mongo_helper.get_next_id("Withdraw")
                currency = "CNY"
                if _type == "2":
                    currency = "TRC20"
                await mongo_helper.insert_one("Withdraw",
                                              {"_id": withdraw_id, "uid": current_user["_id"], "type": _type,
                                               "name": name, "currency": currency,
                                               "bank_name": bank_name, "branch_name": branch_name,
                                               "card_number": card_number, "address_usdt": address_usdt,
                                               "money": money, "real_money": None, "status": "0",
                                               "add_time": now_utc()})
        self.write(res)


class UserCertifiedWithdrawHandler(BaseHandler):
    """
        用户提现审核
        post -> /user/certifiedWithdraw/
        payload:
            {
                "id": "编号",
                "status": "状态 0待审核 1审核成功 2审核失败",
                "money": "实际金额"
            }
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_fail_func(None, message="操作失败")
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")
        status = req_data.get("status")
        money = req_data.get("money")

        # 查询提现记录
        withdraw = await mongo_helper.fetch_one("Withdraw", {"_id": _id})
        if withdraw is not None:
            if status == "1":
                money = abs(float(money))
                await mongo_helper.update_one("Withdraw", {"_id": withdraw["_id"]},
                                              {"$set": {"status": status, "real_money": money}})
                # 审核成功才修改用户余额
                res = await lock_update_user_balance(withdraw["uid"], -money, True)
            elif status == "2":
                await mongo_helper.update_one("Withdraw", {"_id": withdraw["_id"]}, {"$set": {"status": status}})
                money = withdraw["money"]
                # 审核失败，增加用户余额
                res = await lock_update_user_balance(withdraw["uid"], money, False)
            else:
                await mongo_helper.update_one("Withdraw", {"_id": withdraw["_id"]}, {"$set": {"status": status}})
                res = res_func(None)
        self.write(res)
