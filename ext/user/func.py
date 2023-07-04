from tornado import locks

from base.res import res_fail_func, res_func
from base.utils import mongo_helper, now_utc
from core.params.service import ParamService
from core.users.models import User
from core.users.service import UserService

lock = locks.Lock()


async def lock_user_withdraw(uid, money):
    # 在线用户提现，需要审核（并发加锁）
    async with lock:
        user = await mongo_helper.fetch_one(User.collection_name, {"_id": uid})
        if user is not None:
            # 提现
            if user.get("balance", 0) >= money:
                balance = user.get("balance", 0) - money
                await mongo_helper.update_one(User.collection_name, {"_id": uid},
                                              {"$set": {"balance": round(balance, 2)}})
                # 删除缓存
                UserService.delete_cache(uid)
            else:
                return res_fail_func(None, code=11001, message="余额不足")
            return res_func(None)
        else:
            return res_fail_func(None, code=10005, message="用户不存在")


async def lock_update_user_balance(uid, money, is_total):
    # 修改用户余额，判断是否需要增加累计（并发加锁）
    async with lock:
        user = await mongo_helper.fetch_one(User.collection_name, {"_id": uid})
        if user is not None:
            if money > 0:
                # 充值
                balance = user.get("balance", 0) + money
                if is_total:
                    # 累计充值
                    total_recharge = user.get("total_recharge", 0) + money
                    await mongo_helper.update_one(User.collection_name, {"_id": uid}, {
                        "$set": {"balance": round(balance, 2), "total_recharge": round(total_recharge, 2)}})
                else:
                    await mongo_helper.update_one(User.collection_name, {"_id": uid},
                                                  {"$set": {"balance": round(balance, 2)}})
                # 删除缓存
                UserService.delete_cache(uid)
            else:
                # 提现
                if user.get("balance", 0) >= abs(money):
                    balance = user.get("balance", 0) - abs(money)
                    if is_total:
                        # 累计提现
                        total_withdraw = user.get("total_withdraw", 0) + abs(money)
                        await mongo_helper.update_one(User.collection_name, {"_id": uid}, {
                            "$set": {"balance": round(balance, 2), "total_withdraw": round(total_withdraw, 2)}})
                    else:
                        await mongo_helper.update_one(User.collection_name, {"_id": uid},
                                                      {"$set": {"balance": round(balance, 2)}})
                    # 删除缓存
                    UserService.delete_cache(uid)
                else:
                    return res_fail_func(None, code=11001, message="余额不足")
            return res_func(None)
        else:
            return res_fail_func(None, code=10005, message="用户不存在")


async def lock_user_recharge_or_withdraw(_type, uid, money):
    # 后台用户充值或提现（并发加锁）
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
                # 删除缓存
                UserService.delete_cache(uid)
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
                    # 删除缓存
                    UserService.delete_cache(uid)
                else:
                    return res_fail_func(None, code=11001, message="余额不足")
            return res_func(None)
        else:
            return res_fail_func(None, code=10005, message="用户不存在")


async def lock_agent_income(uid, money):
    # 计算代理收益（并发加锁）
    async with lock:
        user = await mongo_helper.fetch_one(User.collection_name, {"_id": uid})
        if user is not None:
            # 判断是否有一级代理
            if user.get("pid") is not None:
                # 获取一级代理
                one = await UserService.get_user_by_id(user.get("pid"))
                if one is not None:
                    level1 = await ParamService.get_param("level1")
                    if level1 is not None:
                        rate = float(level1["value"])
                        # 计算代理收益
                        income = round(money * rate, 2)
                        balance = one.get("balance", 0) + income
                        # 修改余额宝数据
                        await mongo_helper.update_one("User", {"_id": one["_id"]},
                                                      {"$set": {"balance": round(balance, 2)}})
                        # 删除缓存
                        UserService.delete_cache(one["_id"])
                        # 记录收益
                        _id = await mongo_helper.get_next_id("IncomeAgent")
                        await mongo_helper.insert_one("IncomeAgent",
                                                      {"_id": _id, "uid": one["_id"], "level": "1", "money": income,
                                                       "remarks": "uid:" + str(uid) + " 充值" + str(
                                                           money) + "返佣", "add_time": now_utc()})
                        # 判断是否有二级代理
                        if one.get("pid") is not None:
                            # 获取二级代理
                            two = await UserService.get_user_by_id(one.get("pid"))
                            if two is not None:
                                level2 = await ParamService.get_param("level2")
                                if level2 is not None:
                                    rate = float(level2["value"])
                                    # 计算代理收益
                                    income = round(money * rate, 2)
                                    balance = two.get("balance", 0) + income
                                    # 修改余额宝数据
                                    await mongo_helper.update_one("User", {"_id": two["_id"]},
                                                                  {"$set": {"balance": round(balance, 2)}})
                                    # 删除缓存
                                    UserService.delete_cache(two["_id"])
                                    # 记录收益
                                    _id = await mongo_helper.get_next_id("IncomeAgent")
                                    await mongo_helper.insert_one("IncomeAgent",
                                                                  {"_id": _id, "uid": two["_id"], "level": "2",
                                                                   "money": income,
                                                                   "remarks": "uid:" + str(uid) + " 充值" + str(
                                                                       money) + "返佣", "add_time": now_utc()})
                                    # 判断是否有三级代理
                                    if two.get("pid") is not None:
                                        # 获取三级代理
                                        three = await UserService.get_user_by_id(two.get("pid"))
                                        if three is not None:
                                            level3 = await ParamService.get_param("level3")
                                            if level3 is not None:
                                                rate = float(level3["value"])
                                                # 计算代理收益
                                                income = round(money * rate, 2)
                                                balance = three.get("balance", 0) + income
                                                # 修改余额宝数据
                                                await mongo_helper.update_one("User", {"_id": three["_id"]},
                                                                              {"$set": {"balance": round(balance, 2)}})
                                                # 删除缓存
                                                UserService.delete_cache(three["_id"])
                                                # 记录收益
                                                _id = await mongo_helper.get_next_id("IncomeAgent")
                                                await mongo_helper.insert_one("IncomeAgent",
                                                                              {"_id": _id, "uid": three["_id"],
                                                                               "level": "3",
                                                                               "money": income,
                                                                               "remarks": "uid:" + str(
                                                                                   uid) + " 充值" + str(money) + "返佣",
                                                                               "add_time": now_utc()})
