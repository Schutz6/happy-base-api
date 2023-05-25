from tornado.web import url

from core.menus.handler import AddHandler, DeleteHandler, UpdateHandler, ListHandler, GetListHandler

urlpatterns = [
    url('/menu/add/', AddHandler),
    url('/menu/delete/', DeleteHandler),
    url('/menu/update/', UpdateHandler),
    url('/menu/list/', ListHandler),
    url('/menu/getList/', GetListHandler)
]