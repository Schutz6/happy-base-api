import asyncio
import logging
import tornado.web

from apscheduler.schedulers.tornado import TornadoScheduler
from tornado.options import define, options
from apps.tasks.func import run_task
from bases.config import settings
from apps.tasks.models import Task
from bases.utils import mongo_helper
from dbs.func import init_db_data
from routes.urls import urlpatterns

define("port", default=9001, help="运行端口", type=int)
define("debug", default=True, help="以调试模式运行")

""" 设置日志打印格式 """
logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt='%Y/%m/%d  %H:%M:%S %a')


async def init_scheduler():
    """ 初始化定时任务 """
    scheduler = TornadoScheduler()
    scheduler.start()
    # 初始化配置的定时任务
    query = await mongo_helper.fetch_all(Task.collection_name, {"status": 1}, [("_id", -1)])
    for task in query:
        run_task(scheduler, task)
    logging.error('定时任务已初始化')
    return scheduler


def make_app():
    """ 构建一个应用 """
    if settings["run_mode"] == "debug":
        return tornado.web.Application(urlpatterns, debug=options.debug)
    else:
        return tornado.web.Application(urlpatterns)


async def main():
    """ 初始化数据库"""
    await init_db_data()

    """启动应用"""
    app = make_app()
    app.listen(options.port, xheaders=True)
    app.scheduler = await init_scheduler()
    logging.error('基础API服务已启动，端口=' + str(options.port))
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
