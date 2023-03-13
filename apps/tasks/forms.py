from wtforms import StringField, IntegerField

from bases.forms import BaseForm


# 任务表单
class TaskForm(BaseForm):
    name = StringField("任务名称")
    func = StringField("执行方法")
    type = IntegerField("任务类型 1定时任务 2周期任务 3间隔任务")
    exec_data = StringField("定时任务执行时间")
    exec_cron = StringField("周期任务执行时间")
    exec_interval = StringField("间隔任务执行时间")
    status = IntegerField("任务状态 0待启动 1已启动 2已停止")
