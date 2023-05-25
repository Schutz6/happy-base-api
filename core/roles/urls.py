from tornado.web import url

from core.roles.handler import AddHandler, DeleteHandler, UpdateHandler, ListHandler, GetListHandler

urlpatterns = [
    url('/role/add/', AddHandler),
    url('/role/delete/', DeleteHandler),
    url('/role/update/', UpdateHandler),
    url('/role/list/', ListHandler),
    url('/role/getList/', GetListHandler)
]