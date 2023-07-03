import json

from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func
from base.utils import mongo_helper
from core.users.models import User


class InviteListHandler(BaseHandler):
    """
        邀请列表
        post -> /agent/inviteList/
        payload:
            {
               "currentPage": 1,
               "pageSize": 10
            }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)

        current_user = self.current_user

        # 查询条件
        query_criteria = {"pid": current_user["_id"]}

        # 查询分页
        page_data = await mongo_helper.fetch_page_info(User.collection_name, query_criteria, [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(User.collection_name, query_criteria)

        results = []
        for item in page_data.get("list", []):
            results.append({"uid": item["_id"], "add_time": item["add_time"], "balance": item.get("balance", 0)})
        data = {
            "total": total,
            "size": page_size,
            "current": current_page,
            "results": results
        }
        res['data'] = data
        self.write(res)


class AgentIncomeListHandler(BaseHandler):
    """
        代理奖励记录
        post -> /agent/incomeList/
        payload:
           {
               "currentPage": 1,
               "pageSize": 10
           }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)

        current_user = self.current_user

        # 查询条件
        query_criteria = {"uid": current_user["_id"]}

        # 查询分页
        page_data = await mongo_helper.fetch_page_info("IncomeAgent", query_criteria, [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(User.collection_name, query_criteria)

        results = []
        for item in page_data.get("list", []):
            item["id"] = item["_id"]
            results.append(item)
        data = {
            "total": total,
            "size": page_size,
            "current": current_page,
            "results": results
        }
        res['data'] = data
        self.write(res)


class AgentTeamHandler(BaseHandler):
    """
        代理团队
        get -> /agent/team/
    """

    @authenticated_async(None)
    async def get(self):
        res = res_func({})

        current_user = self.current_user

        # 一级列表，一级奖金
        one_list = []
        one_income = 0

        # 二级列表，二级奖金
        two_list = []
        two_income = 0

        # 三级列表，三级奖金
        three_list = []
        three_income = 0

        # 一级团队列表
        ones = await mongo_helper.fetch_all(User.collection_name, {'pid': current_user["_id"]}, [("_id", -1)])
        for one in ones:
            one_list.append({"uid": one["_id"], "total_recharge": one.get("total_recharge", 0), "level": 1})
            # 二级团队列表
            twos = await mongo_helper.fetch_all(User.collection_name, {'pid': one["_id"]}, [("_id", -1)])
            for two in twos:
                two_list.append({"uid": two["_id"], "total_recharge": two.get("total_recharge", 0), "level": 2})
                # 三级团队列表
                threes = await mongo_helper.fetch_all(User.collection_name, {'pid': two["_id"]}, [("_id", -1)])
                for three in threes:
                    three_list.append(
                        {"uid": three["_id"], "total_recharge": three.get("total_recharge", 0), "level": 3})

        # 一级奖金
        query = await mongo_helper.fetch_aggregate("IncomeAgent", [
            {"$match": {"uid": current_user["_id"]}},
            {'$group': {'_id': '$level', 'count': {'$sum': '$money'}}}
        ])
        for item in query:
            if item["_id"] == "1":
                one_income = item["count"]
            elif item["_id"] == "2":
                two_income = item["count"]
            elif item["_id"] == "3":
                three_income = item["count"]
        res["data"] = {"one_list": one_list, "one_income": one_income, "two_list": two_list, "two_income": two_income,
                       "three_list": three_list, "three_income": three_income}
        self.write(res)
