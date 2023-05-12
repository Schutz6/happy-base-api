import asyncio
import time

from apps.logs.models import Log
from bases.utils import mongo_helper


# 插入日志记录
# 10000条数据0.01秒左右
# 100000条数据0.1秒左右
# 1000000条数据15秒左右
async def init_log():
    print("正在插入")
    data_list = []
    # 开始时间
    start_time = round(time.time() * 1000, 2)
    for i in range(100000):
        data_list.append(
            {"_id": i, "username": "匿名", "method": "GET", "uri": "#", "params": "#", "ip": "127.0.0.1", "times": 10})

    # 结束时间
    finish_time1 = round(time.time() * 1000, 2)
    # 访问时间
    times = round(finish_time1 - start_time, 2)
    print(times)
    await mongo_helper.insert_many(Log.collection_name, data_list)
    # 结束时间
    finish_time = round(time.time() * 1000, 2)
    # 访问时间
    times = round(finish_time - start_time, 2)
    print(times)
    print("已完成")


async def db_demo():
    # _id = await mongo_helper.get_next_id('test')
    # print(_id)
    # v = await mongo_helper.get_connections()
    # print(v)
    # v = await mongo_helper.insert_one('test', {"_id": _id, "name": "hello", "price": 33})
    # print(v)
    # v = await mongo_helper.fetch_aggregate('test', [{'$group': {'_id': None, 'count': {'$sum': 1}}}])
    # print(v)
    # v = await mongo_helper.update_one('test', {'_id': 1}, {'$set': {"name": "hello1"}})
    # print(v)
    # v = await mongo_helper.fetch_all('test', {"_id": {"$in": [1, 2]}})
    # print(v)
    v = await mongo_helper.fetch_page_info('test', {}, [("_id", -1)], page_size=2, page_no=2)
    print(v)
    # v = await mongo_helper.fetch_count_info('test', {})
    # print(v)
    # await mongo_helper.drop_collection('test')


if __name__ == '__main__':
    asyncio.run(init_log())
    # asyncio.run(db_demo())
