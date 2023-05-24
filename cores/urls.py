from tornado.web import url

from cores.handler import AddHandler, DeleteHandler, BatchDeleteHandler, UpdateHandler, ListHandler, GetListHandler

urlpatterns = [
    url('/core/add/', AddHandler),
    url('/core/delete/', DeleteHandler),
    url('/core/batchDelete/', BatchDeleteHandler),
    url('/core/update/', UpdateHandler),
    url('/core/list/', ListHandler),
    url('/core/getList/', GetListHandler)
]