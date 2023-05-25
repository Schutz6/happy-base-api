from tornado.web import url

from core.dicts.handler import ListDictTypeHandler, AddDictTypeHandler, DeleteDictTypeHandler, ListDictValueHandler, \
    AddDictValueHandler, DeleteDictValueHandler, GetDictListHandler

urlpatterns = [
    url('/dict/typeList/', ListDictTypeHandler),
    url('/dict/typeAdd/', AddDictTypeHandler),
    url('/dict/typeDelete/', DeleteDictTypeHandler),
    url('/dict/valueList/', ListDictValueHandler),
    url('/dict/valueAdd/', AddDictValueHandler),
    url('/dict/valueDelete/', DeleteDictValueHandler),
    url('/dict/getList/', GetDictListHandler)
]
