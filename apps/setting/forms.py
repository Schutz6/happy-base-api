from wtforms import StringField

from bases.forms import BaseForm


# 系统设置
class SettingForm(BaseForm):
    content = StringField("设置内容")
