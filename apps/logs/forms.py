from wtforms import StringField

from bases.forms import BaseForm


# 日志表单
class LogForm(BaseForm):
    username = StringField("账号")
    ip = StringField("IP")

