from tornado.web import url

from apps.logs.handler import ClearHandler, BatchDeleteHandler, ListHandler

urlpatterns = [
    url('/log/clear/', ClearHandler),
    url('/log/batchDelete/', BatchDeleteHandler),
    url('/log/list/', ListHandler),
]
