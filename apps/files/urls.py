from tornado.web import url

from apps.files.handler import UploadHandler, HeadUploadHandler, ListHandler

urlpatterns = [
    url('/file/upload/', UploadHandler),
    url('/file/upload/head/', HeadUploadHandler),
    url('/file/list/', ListHandler)
]
