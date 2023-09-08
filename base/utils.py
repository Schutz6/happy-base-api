import hashlib
import logging
import random
import time

import redis
import motor.motor_asyncio

from pymongo import ReturnDocument
from config import settings
from datetime import datetime, timedelta
from urllib.parse import urlparse


class RedisHelper(object):
    def __init__(self):
        # 创建连接池
        self.pool = redis.ConnectionPool(host=settings['redis']['host'], port=settings['redis']['port'],
                                         password=settings['redis']['password'],
                                         decode_responses=True)
        # 创建链接对象
        self.redis = redis.Redis(connection_pool=self.pool)


class MongoHelper(object):
    """封装 MongoDB 的基本操作"""

    def __init__(self):
        """实例化 MongoDB 的连接池对象,使用对象进行 MongoDB 的操作"""
        if settings["mongo"].get("password") is None:
            url = "mongodb://%(host)s:%(port)s" % {
                "host": settings["mongo"]['host'],
                "port": settings["mongo"]['port']
            }
        else:
            # 扩展有密码时连接的配置信息
            url = "mongodb://%(user)s:%(password)s@%(host)s:%(port)s" % {
                "user": settings["mongo"]["user"],
                "password": settings["mongo"]["password"],
                "host": settings["mongo"]["host"],
                "port": settings["mongo"]["port"]
            }
        # 将线程安全的连接池封装到对象中
        self.connect_client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.db = self.connect_client[settings["mongo"]['database']]

    async def get_connections(self) -> list:
        """
        获取数据库中的集合信息
        :return: list 集合名称的列表信息

        example:
            v = await mongo_helper.get_connections()
            print(v)
        """
        return await self.db.list_collection_names()

    async def get_next_id(self, collection_name: str):
        """
        返回一个自增长ID
        :param collection_name: str 集合的名称
        :return: 返回 自增长id

        example:
            v = await mongo_helper.get_next_id('test')
            print(v)
        """
        res = await self.db[collection_name].find_one_and_update({"_id": "sequence_id"}, {"$inc": {"seq": 1}},
                                                                 projection={'seq': True, '_id': False},
                                                                 return_document=ReturnDocument.AFTER)
        if res is not None:
            next_id = res["seq"]
        else:
            await self.db[collection_name].insert_one({"_id": "sequence_id", "seq": 1})
            next_id = 1
        return next_id

    async def insert_one(self, collection_name: str, value: dict):
        """
        向集合中插入一条(文档)数据
        :param collection_name: str 集合的名称
        :param value: 被插入的数据信息
        :return: 返回插入返回的 id 信息

        example:
            v = await mongo_helper.insert_one('test', {"name": "hello", "price": 33})
            print(v)
        """
        col_insert = await self.db[collection_name].insert_one(value)
        col_id = col_insert.inserted_id
        return col_id

    async def insert_one_session(self, collection_name: str, value: dict, session):
        """
        向集合中插入一条(文档)数据
        :param collection_name: str 集合的名称
        :param value: 被插入的数据信息
        :param session 事务控制
        :return: 返回插入返回的 id 信息

        example:
            v = await mongo_helper.insert_one('test', {"name": "hello", "price": 33}, session)
            print(v)
        """
        col_insert = await self.db[collection_name].insert_one(value, session=session)
        col_id = col_insert.inserted_id
        return col_id

    async def insert_many(self, collection_name: str, value: list):
        """
        插入多条数据信息
        :param collection_name: 集合的名称
        :param value: 列表嵌套字典的信息
        :return: 返回插入的 ids 对象集合的列表信息

        example:
            data = [
                {"name": "前端", 'price': 66},
                {"name": "前端", 'price': 66}
            ]
            v = mongo_helper.insert_many('test', data)
            print(v)
        """
        col_insert = await self.db[collection_name].insert_many(value)
        col_ids = col_insert.inserted_ids
        return col_ids

    async def insert_many_session(self, collection_name: str, value: list, session):
        """
        插入多条数据信息
        :param collection_name: 集合的名称
        :param value: 列表嵌套字典的信息
        :param session 事务控制
        :return: 返回插入的 ids 对象集合的列表信息

        example:
            data = [
                {"name": "前端", 'price': 66},
                {"name": "前端", 'price': 66}
            ]
            v = mongo_helper.insert_many('test', data)
            print(v)
        """
        col_insert = await self.db[collection_name].insert_many(value, session=session)
        col_ids = col_insert.inserted_ids
        return col_ids

    async def fetch_one(self, collection_name: str, filters: dict = None) -> dict:
        """
        查询一条符合条件的数据信息
        :param collection_name: 集合的名称
        :param filters: dict; 过滤条件
        :return: dict; 筛选结果,字典信息

        example:
            filters = {"name": "python入门"}
            v = mongo_helper.fetch_one("test", filters)
            print(v)

        """
        result = await self.db[collection_name].find_one(filters)
        return result

    async def fetch_all(self, collection_name: str, filters: dict = None, sort_data=None) -> list:
        """
        查询符合条件的所有数据信息,将游标的信息进行循环获取到列表信息
        :param collection_name: 集合的名称
        :param filters: dict; 过滤的条件信息
        :param sort_data: 排序条件
        :return: list; 符合条件的数据列表

        example:
            filters = {"name": "java入门"}
            v = mongo_helper.fetch_all("test", filters)
            print(v, type(v))

        """
        cursor = self.db[collection_name].find(filters).sort(sort_data)
        result = await cursor.to_list(length=None)
        result_list = [i for i in result]
        return result_list

    async def fetch_page_info(self, collection_name: str, filters: dict = None, sort_data=None,
                              page_size: int = 10,
                              page_no: int = 1) -> dict:
        """
        分页查询的使用
        :param collection_name: 集合的名称信息
        :param filters: 查询条件信息
        :param sort_data: 排序条件
        :param page_size: 每页上的数量信息
        :param page_no: 页码信息
        :return: dict; 返回分页查询的信息数据

        example:
            filters = {"name": "java入门"}
            v = mongo_helper.fetch_page_info("test", filters, 5, 5)
            print(v)
        """
        if sort_data is None:
            sort_data = [("_id", -1)]
        skip = page_size * (page_no - 1)
        cursor = self.db[collection_name].find(filters).sort(sort_data).limit(page_size).skip(skip)
        result = await cursor.to_list(length=None)
        result_dict = {"page_size": page_size, "page_no": page_no, "list": [i for i in result]}
        return result_dict

    async def fetch_count_info(self, collection_name: str, filters: dict = None) -> int:
        """
        查询统计集合中的文档的数量信息
        :param collection_name: str; 集合的名称
        :param filters: dict; 按条件统计,为空的时候查询全部的信息
        :return: int; 集合中的文档的数量信息

        example:
            v = mongo_helper.fetch_count_info("test")
            print(v, type(v))
        """
        if filters is None:
            filters = {}
        result = await self.db[collection_name].count_documents(filters)
        return result

    async def fetch_aggregate(self, collection_name: str, filters: list = None) -> list:
        """
        统计符合条件的所有数据信息,将游标的信息进行循环获取到列表信息
        :param collection_name: 集合的名称
        :param filters: dict; 过滤的条件信息
        :return: list 符合条件的数据列表

        example:
            filters = [{"$match": {'_id': 1}}, {'$group': {'_id': '$_id', 'count': {'$sum': 1}}}]
            v = mongo_helper.fetch_aggregate("test", filters)
            print(v, type(v))

        """
        cursor = self.db[collection_name].aggregate(filters)
        result = await cursor.to_list(length=None)
        result_list = [i for i in result]
        return result_list

    async def update_one(self, collection_name: str, filters: dict, data: dict) -> int:
        """
        更新一条文档的信息
        :param collection_name: 集合的名称
        :param filters: dict; 筛选条件
        :param data: 修改的信息
        :return: int; 返回被修改的文档数

        example:
            filters = {"name": "java入门"}
            v = mongo_helper.update_one("test", filters, {"$set": {"name": "我爱学习"}})
            print(v, type(v))
        """
        result = await self.db[collection_name].update_one(filters, data)
        return result.modified_count

    async def update_one_session(self, collection_name: str, filters: dict, data: dict, session) -> int:
        """
        更新一条文档的信息
        :param collection_name: 集合的名称
        :param filters: dict; 筛选条件
        :param data: 修改的信息
        :param session: 事务控制
        :return: int; 返回被修改的文档数

        example:
            filters = {"name": "java入门"}
            v = mongo_helper.update_one_session("test", filters, {"$set": {"name": "我爱学习"}})
            print(v, type(v))
        """
        result = await self.db[collection_name].update_one(filters, data, session=session)
        return result.modified_count

    async def update_or_add_one(self, collection_name: str, filters: dict, data: dict) -> int:
        """
        更新或新增一条文档的信息
        :param collection_name: 集合的名称
        :param filters: dict; 筛选条件
        :param data: 修改的信息
        :return: int; 返回被修改的文档数

        example:
            filters = {"name": "java入门"}
            v = mongo_helper.update_or_add_one("test", filters, {"$set": {"name": "我爱学习"}})
            print(v, type(v))
        """
        result = await self.db[collection_name].find_one_and_update(filters, data)
        return result.modified_count

    async def update_or_add_one_session(self, collection_name: str, filters: dict, data: dict, session) -> int:
        """
        更新或新增一条文档的信息
        :param collection_name: 集合的名称
        :param filters: dict; 筛选条件
        :param data: 修改的信息
        :param session: 事务控制
        :return: int; 返回被修改的文档数

        example:
            filters = {"name": "java入门"}
            v = mongo_helper.update_or_add_one_session("test", filters, {"$set": {"name": "我爱学习"}}, session)
            print(v, type(v))
        """
        result = await self.db[collection_name].find_one_and_update(filters, data, session=session)
        return result.modified_count

    async def update_many(self, collection_name: str, filters: dict, data: dict) -> int:
        """
        批量修改数据
        :param collection_name: 集合的名称
        :param filters: 筛选条件
        :param data: 修改信息
        :return: int; 修改的数量

        example:
            filters = {"name": "我爱学习"}
            v = mongo_helper.update_many("test", filters, {"$set": {"name": "批量修改回来"}})
            print(v, type(v))
        """
        result = await self.db[collection_name].update_many(filters, data)
        return result.modified_count

    async def update_many_session(self, collection_name: str, filters: dict, data: dict, session) -> int:
        """
        批量修改数据
        :param collection_name: 集合的名称
        :param filters: 筛选条件
        :param data: 修改信息
        :param session: 事务控制
        :return: int; 修改的数量

        example:
            filters = {"name": "我爱学习"}
            v = mongo_helper.update_many_session("test", filters, {"$set": {"name": "批量修改回来"}}, session)
            print(v, type(v))
        """
        result = await self.db[collection_name].update_many(filters, data, session=session)
        return result.modified_count

    async def delete_one(self, collection_name: str, filters: dict) -> int:
        """
        删除单条的数据信息
        :param collection_name:
        :param filters:
        :return: int; 删除数据的条数

        example:
            filters = {"name": "批量修改回来"}
            v = mongo_helper.delete_one("test", filters)
            print(v, type(v))
        """
        result = await self.db[collection_name].delete_one(filters)
        return result.deleted_count

    async def delete_one_session(self, collection_name: str, filters: dict, session) -> int:
        """
        删除单条的数据信息
        :param collection_name:
        :param filters:
        :param session: 事务控制
        :return: int; 删除数据的条数

        example:
            filters = {"name": "批量修改回来"}
            v = mongo_helper.delete_one_session("test", filters, session)
            print(v, type(v))
        """
        result = await self.db[collection_name].delete_one(filters, session=session)
        return result.deleted_count

    async def delete_many(self, collection_name: str, filters: dict) -> int:
        """
        删除多条的数据信息
        :param collection_name: 集合的名称
        :param filters: dict 过滤条件
        :return: int 返回删除的条数

        example:
            filters = {"name": "批量修改回来"}
            v = mongo_helper.delete_many("test", filters)
            print(v, type(v))

        """
        result = await self.db[collection_name].delete_many(filters)
        return result.deleted_count

    async def delete_many_session(self, collection_name: str, filters: dict, session) -> int:
        """
        删除多条的数据信息
        :param collection_name: 集合的名称
        :param filters: dict 过滤条件
        :param session: 事务控制
        :return: int 返回删除的条数

        example:
            filters = {"name": "批量修改回来"}
            v = mongo_helper.delete_many_session("test", filters, session)
            print(v, type(v))

        """
        result = await self.db[collection_name].delete_many(filters, session=session)
        return result.deleted_count

    async def drop_collection(self, collection_name: str):
        """
        删除集合(删除表)
        :param collection_name: 集合的名称
        :return: None

        example:
            mongo_helper.drop_collection("test_data")
        """
        await self.db[collection_name].drop()

    async def drop_collection_session(self, collection_name: str, session):
        """
        删除集合(删除表)
        :param collection_name: 集合的名称
        :param session: 事务控制
        :return: None

        example:
            mongo_helper.drop_collection_session("test_data", session)
        """
        await self.db[collection_name].drop(session=session)


""" 单例对象 """
mongo_helper = MongoHelper()
redis_helper = RedisHelper()


# 获取md5值
def get_md5(value):
    m = hashlib.md5()
    m.update(value.encode("utf8"))
    return m.hexdigest()


# 获取随机头像
def get_random_head():
    return '#URL#/avatars/default.png'


# 打印错误日志
def show_error_log(msg):
    logging.error(msg)


# 格式化时间
def format_time(_time, fmt):
    return datetime.fromtimestamp(_time / 1000).strftime(fmt)


# 字符串转时间戳
def to_timestamp(_time_str):
    return int(datetime.strptime(_time_str, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)


# 获取UTC时间戳
def now_utc():
    return int(datetime.utcnow().timestamp() * 1000)


# 获取本地时间戳
def now_local():
    return int(datetime.now().timestamp() * 1000)


# 本地时间转UTC时间戳
def local_to_utc(_time):
    return int(datetime.utcfromtimestamp(_time / 1000).timestamp() * 1000)


# UTC时间转本地时间戳
def utc_to_local(_utctime):
    local_tm = datetime.fromtimestamp(0)
    utc_tm = datetime.utcfromtimestamp(0)
    offset = local_tm - utc_tm
    return int((datetime.fromtimestamp(_utctime / 1000) + offset).timestamp() * 1000)


# 获取上n分钟（UTC）
def now_last_minute(minute):
    # 当前时间
    old_time = datetime.now()
    # 减去n分钟
    add_time = timedelta(minutes=minute)
    # 增加后时间
    return local_to_utc((old_time + add_time).timestamp() * 1000)


# 获取增加/减少天数时间
def get_add_time(_utctime, days):
    # 原时间(utc转本地时间)
    old_time = datetime.fromtimestamp(utc_to_local(_utctime) / 1000)
    # 增加时间
    add_time = timedelta(days=days)
    # 增加后时间
    return local_to_utc((old_time + add_time).timestamp() * 1000)


# 比较时间的大小
def time_cmp(first_time, second_time):
    return first_time > second_time


# 获取唯一的账单编号
def get_order_no(module):
    return module + "-" + str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + get_random(4)


# 获取随机数(数字+字母)
def get_random(num):
    seeds = '123456789abcdefghjkmnopqrstuvwxy'
    code = []
    for i in range(num):
        code.append(random.choices(seeds)[0])
    return ''.join(code)


# 获取随机数（数字）
def get_random_num(num):
    seeds = '123456789'
    code = []
    for i in range(num):
        code.append(random.choices(seeds)[0])
    return ''.join(code)


# 替换域名地址
def replace_url(domain, url):
    # 将url中原域名去掉
    url_obj = urlparse(url)
    # 拼接上新的域名
    return domain + url_obj.path
