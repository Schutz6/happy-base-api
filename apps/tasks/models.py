from bases.utils import mongo_helper


class Task(object):
    """定时任务"""

    # 文档名
    collection_name = "Task"

    """数据库字段说明"""
    # 任务名称
    name = None
    # 执行方法
    func = None
    # 任务类型 2cron任务 3间隔任务
    type = 0
    # 周期任务执行时间
    exec_cron = None
    # 间隔任务执行时间
    exec_interval = None
    # 任务状态 0待启动 1已启动 2已停止
    status = 0
    # 配置参数
    options = None

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Task.collection_name)
        return {"_id": _id,
                "name": req_data.get("name"),
                "func": req_data.get("func"),
                "type": req_data.get("type", 0),
                "exec_cron": req_data.get("exec_cron"),
                "exec_interval": req_data.get("exec_interval"),
                "status": req_data.get("status", 0),
                "options": req_data.get("options")}
