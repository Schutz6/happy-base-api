from tornado.web import url

from apps.dict.handler import ListDictTypeHandler, AddDictTypeHandler, DeleteDictTypeHandler, ListDictValueHandler, \
    AddDictValueHandler, DeleteDictValueHandler, GetDictListHandler

urlpatterns = [
    url('/dictType/list/', ListDictTypeHandler),
    url('/dictType/add/', AddDictTypeHandler),
    url('/dictType/delete/', DeleteDictTypeHandler),
    url('/dictValue/list/', ListDictValueHandler),
    url('/dictValue/add/', AddDictValueHandler),
    url('/dictValue/delete/', DeleteDictValueHandler),
    url('/dict/getList/', GetDictListHandler)
]
