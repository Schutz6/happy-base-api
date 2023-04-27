from datetime import datetime
from apps.users.models import User
from bases.decorators import authenticated_admin_async
from bases.handler import BaseHandler
from bases.res import resFunc
from bases.utils import now_utc, format_time, to_timestamp, get_add_time


class StatisticsUserHandler(BaseHandler):
    '''
        统计用户数据
        get -> /statistics/user/
    '''

    @authenticated_admin_async
    async def get(self):
        res = resFunc({})
        data = {"total_users": 0, "today_users": 0, "yesterday_users": 0, "month_users": 0}
        user_db = User()

        # 今日日期
        today = format_time(now_utc(), '%Y-%m-%d')
        # 昨日日期
        yesterday = format_time(get_add_time(now_utc(), -1), '%Y-%m-%d')
        # 一个月开始日期
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")

        # 总会员数
        query = user_db.aggregate([
            {"$match": {"roles": ['user']}},
            {'$group': {'_id': None, 'count': {'$sum': 1}}}
        ])
        for item in query:
            data["total_users"] += item["count"]

        # 今日新增会员数
        query = user_db.aggregate([
            {"$match": {"roles": ['user'], 'add_time': {"$gt": to_timestamp(today + " 00:00:00"),
                                                        "$lt": to_timestamp(today + " 23:59:59")}}},
            {'$group': {'_id': None, 'count': {'$sum': 1}}}
        ])
        for item in query:
            data["today_users"] += item["count"]

        # 昨日新增会员数
        query = user_db.aggregate([
            {"$match": {"roles": ['user'], 'add_time': {"$gt": to_timestamp(yesterday + " 00:00:00"),
                                                        "$lt": to_timestamp(yesterday + " 23:59:59")}}},
            {'$group': {'_id': None, 'count': {'$sum': 1}}}
        ])
        for item in query:
            data["yesterday_users"] += item["count"]

        # 本月新增会员数
        query = user_db.aggregate([
            {"$match": {"roles": ['user'], 'add_time': {"$gt": to_timestamp(month_start + " 00:00:00"),
                                                        "$lt": to_timestamp(today + " 23:59:59")}}},
            {'$group': {'_id': None, 'count': {'$sum': 1}}}
        ])
        for item in query:
            data["month_users"] += item["count"]

        res["data"] = data
        self.write(res)
