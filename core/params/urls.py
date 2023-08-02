from tornado.web import url

from core.params.handler import GetListHandler

urlpatterns = [
    url('/param/getList/', GetListHandler)
]