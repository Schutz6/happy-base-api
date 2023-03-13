from tornado.web import url

from apps.tasks.handler import AddHandler, DeleteHandler, UpdateHandler, ListHandler, StartTaskHandler, EndTaskHandler

urlpatterns = [
    url('/task/add/', AddHandler),
    url('/task/delete/', DeleteHandler),
    url('/task/update/', UpdateHandler),
    url('/task/list/', ListHandler),
    url('/task/start/', StartTaskHandler),
    url('/task/end/', EndTaskHandler)
]