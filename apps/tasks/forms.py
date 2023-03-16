from wtforms import StringField, IntegerField

from bases.forms import BaseForm


# 任务表单
class TaskForm(BaseForm):
    name = StringField("任务名称")
    func = StringField("执行方法")
    type = IntegerField("任务类型")
    exec_cron = StringField("周期任务执行时间")
    exec_interval = StringField("间隔任务执行时间")
    status = IntegerField("任务状态")
    options = StringField("配置参数")
