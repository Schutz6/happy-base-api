from tornado.web import url

from core.menus.handler import GetListHandler

urlpatterns = [
    url('/menu/getList/', GetListHandler)
]