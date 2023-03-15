from wtforms import StringField, IntegerField

from bases.forms import BaseForm


# 参数表单
class ParamForm(BaseForm):
    key = StringField("唯一ID")
    value = StringField("参数值")
    remarks = StringField("备注")
    status = IntegerField("状态")
