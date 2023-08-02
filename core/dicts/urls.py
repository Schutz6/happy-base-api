from tornado.web import url

from core.dicts.handler import GetDictListHandler

urlpatterns = [
    url('/dict/getList/', GetDictListHandler)
]
