import asyncio
import base64

from tornado import locks
from tornado.httpclient import AsyncHTTPClient
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


async def download_img():
    # 下载图片，并转成base64
    http_client = AsyncHTTPClient()
    response = await http_client.fetch("https://xxxxxx/xx.jpg")
    print(base64.b64encode(response.buffer.read()).decode("utf8"))


if __name__ == '__main__':
    # 启动测试代码
    # asyncio.run(demo())
    asyncio.run(download_img())
