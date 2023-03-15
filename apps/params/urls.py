from tornado.web import url

from apps.params.handler import AddHandler, DeleteHandler, UpdateHandler, ListHandler, GetListHandler

urlpatterns = [
    url('/param/add/', AddHandler),
    url('/param/delete/', DeleteHandler),
    url('/param/update/', UpdateHandler),
    url('/param/list/', ListHandler),
    url('/param/getList/', GetListHandler)
]