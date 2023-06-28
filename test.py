import asyncio

from tornado import locks
from base.utils import mongo_helper

lock = locks.Lock()


async def demo_transaction():
    # 事务控制代码
    async with await mongo_helper.connect_client.start_session() as s:
        async with s.start_transaction():
            await mongo_helper.insert_one_session("Demo", {"name": "张三", "sex": "男"}, s)
            await mongo_helper.insert_one_session("Demo", {"name": "李四", "sex": "女"}, s)
            raise Exception("出错了")


async def demo_concurrency():
    # 并发加锁代码
    async with lock:
        user = await mongo_helper.fetch_one("User", {"_id": 100001})
        balance = user.get("balance", 0)
        balance += 1
        await mongo_helper.update_one("User", {"_id": 100001}, {"$set": {"balance": balance}})


async def demo():
    # 事务代码
    await demo_transaction()


if __name__ == '__main__':
    # 启动测试代码
    asyncio.run(demo())
