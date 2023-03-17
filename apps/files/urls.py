from tornado.web import url

from apps.files.handler import UploadHandler, HeadUploadHandler, ListHandler, DeleteHandler, BatchDeleteHandler

urlpatterns = [
    url('/file/upload/', UploadHandler),
    url('/file/upload/head/', HeadUploadHandler),
    url('/file/list/', ListHandler),
    url('/file/delete/', DeleteHandler),
    url('/file/batchDelete/', BatchDeleteHandler)
]
