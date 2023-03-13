from wtforms import StringField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired

from bases.forms import BaseForm


# 登录表单
class LoginForm(BaseForm):
    username = StringField("用户名")
    password = StringField("密码")


# 用户表单
class UserForm(BaseForm):
    name = StringField("昵称")
    username = StringField("用户名")
    email = StringField("邮箱")
    mobile = StringField("手机号")
    password = StringField("密码")
    gender = StringField("性别")
    introduction = StringField("个人简介")
    birthday = StringField("生日")
    address = StringField("地址")
    roles = SelectMultipleField("角色")
    avatar = StringField("头像")
    status = IntegerField("状态")


# 修改密码表单
class ChangePwdForm(BaseForm):
    oldPassword = StringField('旧密码')
    newPassword = StringField('新密码', validators=[
        DataRequired(message='请输入新密码')
    ])

