from tornado import locks

from base.res import res_fail_func, res_func
from base.utils import mongo_helper, now_utc
from core.users.models import User
from core.users.service import UserService

lock = locks.Lock()


async def lock_user_recharge_or_withdraw(_type, uid, money):
    # 用户充值或提现（并发加锁）
    async with lock:
        user = await mongo_helper.fetch_one(User.collection_name, {"_id": uid})
        if user is not None:
            # 判断充值还是提现
            if money > 0:
                # 充值
                balance = user.get("balance", 0) + money
                # 累计充值
                total_recharge = user.get("total_recharge", 0) + money
                await mongo_helper.update_one(User.collection_name, {"_id": uid}, {
                    "$set": {"balance": round(balance, 2), "total_recharge": round(total_recharge, 2)}})
                # 生成充值记录
                recharge_id = await mongo_helper.get_next_id("Recharge")
                await mongo_helper.insert_one("Recharge",
                                              {"_id": recharge_id, "uid": uid, "type": _type, "currency": "CNY",
                                               "money": money, "real_money": money, "status": "1",
                                               "add_time": now_utc()})
            elif money < 0:
                # 提现
                if user.get("balance", 0) >= abs(money):
                    balance = user.get("balance", 0) - abs(money)
                    # 累计提现
                    total_withdraw = user.get("total_withdraw", 0) + abs(money)
                    await mongo_helper.update_one(User.collection_name, {"_id": uid}, {
                        "$set": {"balance": round(balance, 2), "total_withdraw": round(total_withdraw, 2)}})
                    # 生成提现记录
                    withdraw_id = await mongo_helper.get_next_id("Withdraw")
                    await mongo_helper.insert_one("Withdraw",
                                                  {"_id": withdraw_id, "uid": uid, "type": _type, "currency": "CNY",
                                                   "money": abs(money), "real_money": abs(money), "status": "1",
                                                   "add_time": now_utc()})
                else:
                    return res_fail_func(None, code=11001, message="余额不足")
            # 删除缓存
            UserService.delete_cache(uid)
            return res_func(None)
        else:
            return res_fail_func(None, code=10005, message="用户不存在")
