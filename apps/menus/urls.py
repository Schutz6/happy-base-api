from tornado.web import url

from apps.menus.handler import AddHandler, DeleteHandler, UpdateHandler, ListHandler, GetListHandler

urlpatterns = [
    url('/menu/add/', AddHandler),
    url('/menu/delete/', DeleteHandler),
    url('/menu/update/', UpdateHandler),
    url('/menu/list/', ListHandler),
    url('/menu/getList/', GetListHandler)
]