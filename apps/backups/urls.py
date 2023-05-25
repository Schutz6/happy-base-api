from tornado.web import url

from apps.backups.handler import DumpHandler, RestoreHandler, DeleteHandler, ListHandler

urlpatterns = [
    url('/backup/dump/', DumpHandler),
    url('/backup/restore/', RestoreHandler),
    url('/backup/delete/', DeleteHandler),
    url('/backup/list/', ListHandler)
]