from wtforms import StringField

from bases.forms import BaseForm


# 角色表单
class RoleForm(BaseForm):
    name = StringField("角色")
    describe = StringField("描述")
