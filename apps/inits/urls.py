from tornado.web import url

from apps.inits.handler import InitDataHandler

urlpatterns = [
    url('/init/data/', InitDataHandler)
]