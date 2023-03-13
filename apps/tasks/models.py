from bases.models import MongoModel
from bases.settings import settings
from bases.utils import now


# 任务
class Task(MongoModel):

    def __init__(self):
        super(Task, self).__init__(settings['mongo']['name'], "Task")

    """数据库字段说明"""
    # 任务名称
    name = None
    # 执行方法
    func = None
    # 任务类型 1定时任务 2周期任务 3间隔任务
    type = 0
    # 定时任务执行时间
    exec_data = None
    # 周期任务执行时间
    exec_cron = None
    # 间隔任务执行时间
    exec_interval = None
    # 任务状态 0待启动 1已启动 2已停止 3已执行
    status = 0

    # 格式化json
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "name": self.name,
                "func": self.func,
                "type": self.type,
                "exec_data": self.exec_data,
                "exec_cron": self.exec_cron,
                "exec_interval": self.exec_interval,
                "status": self.status,
                "add_time": now()}
