from tornado.web import url

from core.codes.handler import AddHandler, DeleteHandler, UpdateHandler, ListHandler, GetModuleHandler

urlpatterns = [
    url('/code/add/', AddHandler),
    url('/code/delete/', DeleteHandler),
    url('/code/update/', UpdateHandler),
    url('/code/list/', ListHandler),
    url('/code/getModule/', GetModuleHandler)
]
