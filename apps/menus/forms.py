from wtforms import StringField, IntegerField, SelectMultipleField

from bases.forms import BaseForm


# 菜单表单
class MenuForm(BaseForm):
    pid = IntegerField("父ID")
    name = StringField("名称")
    icon = StringField("图标")
    url = StringField("地址")
    roles = SelectMultipleField("角色")
    level = IntegerField("层级")
    sort = IntegerField("排序")
    status = IntegerField("状态")
