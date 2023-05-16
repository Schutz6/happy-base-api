from tornado.web import url

from apps.blacklist.handler import DeleteHandler, BatchDeleteHandler, ListHandler

urlpatterns = [
    url('/blacklist/delete/', DeleteHandler),
    url('/blacklist/batchDelete/', BatchDeleteHandler),
    url('/blacklist/list/', ListHandler)
]
