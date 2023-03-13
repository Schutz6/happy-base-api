import asyncio
import logging

import tornado.web
import wtforms_json
from apscheduler.schedulers.tornado import TornadoScheduler

from tornado.options import define, options

from bases.settings import settings
from apps.tasks.models import Task
from routes.urls import urlpatterns

define("port", default=9001, help="运行端口", type=int)
define("debug", default=True, help="以调试模式运行")

# 设置日志打印格式
logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d  %H:%M:%S %a')


# 初始化定时任务
async def init_scheduler():
    scheduler = TornadoScheduler()
    scheduler.start()
    # 查询数据
    task_db = Task()
    query = await task_db.find_all({"_id": {"$ne": "sequence_id"}, "status": 1})
    for task in query:
        job_id = task["_id"]
        if task['type'] == 1:
            # 定时任务类型
            scheduler.add_job(task['func'], 'date', run_date=task['exec_data'], id=str(job_id),
                              args=[str(job_id)])
        elif task['type'] == 2:
            # 周期任务类型
            exec_cron = task['exec_cron']
            hour = exec_cron[0:2]
            minute = exec_cron[3:5]
            scheduler.add_job(task['func'], 'cron', hour=int(hour),
                              minute=int(minute), id=str(job_id),
                              args=[str(job_id)])
        elif task['type'] == 3:
            # 间隔任务类型
            seconds = task['exec_interval']
            scheduler.add_job(task['func'], 'interval', seconds=int(seconds),
                              id=str(job_id),
                              args=[str(job_id)])
    logging.error('定时任务已初始化')
    return scheduler


# 构建一个应用
def make_app():
    if settings["run_mode"] == "debug":
        return tornado.web.Application(urlpatterns, debug=options.debug)
    else:
        return tornado.web.Application(urlpatterns)


async def main():
    wtforms_json.init()
    app = make_app()
    app.listen(options.port, xheaders=True)
    app.scheduler = await init_scheduler()
    logging.error('基础API服务已启动，端口=' + str(options.port))
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
