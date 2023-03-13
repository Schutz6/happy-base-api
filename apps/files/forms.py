from wtforms import StringField, IntegerField

from bases.forms import BaseForm


# 文件表单
class FileForm(BaseForm):
    name = StringField("文件名称")
    status = IntegerField("文件状态 1临时 2永存")
