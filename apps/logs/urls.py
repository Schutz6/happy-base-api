from tornado.web import url

from apps.logs.handler import ClearHandler, ListHandler

urlpatterns = [
    url('/log/clear/', ClearHandler),
    url('/log/list/', ListHandler),
]
