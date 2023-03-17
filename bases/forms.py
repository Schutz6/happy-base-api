from wtforms import StringField, IntegerField, SelectMultipleField
from wtforms_tornado import Form


# 基础表单
class BaseForm(Form):
    id = IntegerField("编号")
    ids = SelectMultipleField("多选ID")
    pageSize = IntegerField("大小")
    currentPage = IntegerField("当前页")
    searchKey = StringField("搜索关键字")
    by = StringField("排序")
