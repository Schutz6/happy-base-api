import json

from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_fail_func, res_func
from base.utils import mongo_helper
from ext.user.func import lock_update_user_balance, lock_agent_income


class UserCertifiedRechargeHandler(BaseHandler):
    """
        用户充值审核
        post -> /user/certifiedRecharge/
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

        # 查询充值记录
        recharge = await mongo_helper.fetch_one("Recharge", {"_id": _id})
        if recharge is not None:
            if status == "1":
                money = abs(float(money))
                await mongo_helper.update_one("Recharge", {"_id": recharge["_id"]},
                                              {"$set": {"status": status, "real_money": money}})
                # 审核成功才修改用户余额
                res = await lock_update_user_balance(recharge["uid"], money, True)
                # 计算代理收益
                await lock_agent_income(recharge["uid"], recharge["money"])
            else:
                await mongo_helper.update_one("Recharge", {"_id": recharge["_id"]}, {"$set": {"status": status}})
                res = res_func(None)
        self.write(res)
