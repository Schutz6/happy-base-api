from tornado.web import url

from apps.setting.handler import SaveHandler, InfoHandler

urlpatterns = [
    url('/setting/save/', SaveHandler),
    url('/setting/getInfo/', InfoHandler)
]