from wtforms import StringField

from bases.forms import BaseForm


# 角色表单
class RoleForm(BaseForm):
    name = StringField("唯一ID")
    describe = StringField("角色")
    remarks = StringField("备注")
