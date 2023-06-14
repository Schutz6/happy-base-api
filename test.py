import asyncio

from base.utils import mongo_helper


async def demo_transaction():
    # 事务测试代码
    async with await mongo_helper.connect_client.start_session() as s:
        async with s.start_transaction():
            await mongo_helper.insert_one_session("Demo", {"name": "张三", "sex": "男"}, s)
            await mongo_helper.insert_one_session("Demo", {"name": "李四", "sex": "女"}, s)
            raise Exception("出错了")

if __name__ == '__main__':
    # 事务代码
    asyncio.run(demo_transaction())
