from wtforms import StringField, IntegerField

from bases.forms import BaseForm


# 字典类型表单
class DictTypeForm(BaseForm):
    name = StringField('类型名称')
    describe = StringField('类型描述')


# 字典值表单
class DictValueForm(BaseForm):
    dict_tid = IntegerField('字典类型编号')
    dict_name = StringField('字典名称')
    dict_value = StringField("字典值")
    sort = IntegerField('自定义排序')
