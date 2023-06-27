from tornado.web import url

from core.users.handler import AddHandler, DeleteHandler, BatchDeleteHandler, UpdateHandler, ListHandler
from core.users.handler_auth import LoginHandler, UserHandler, LogoutHandler, ChangePwdHandler, RefreshLoginHandler

urlpatterns = [
    # 用户认证
    url('/login/', LoginHandler),
    url('/user/', UserHandler),
    url('/logout/', LogoutHandler),
    url('/changePwd/', ChangePwdHandler),
    url('/refreshLogin/', RefreshLoginHandler),

    # 用户模块
    url('/user/add/', AddHandler),
    url('/user/delete/', DeleteHandler),
    url('/user/batchDelete/', BatchDeleteHandler),
    url('/user/update/', UpdateHandler),
    url('/user/list/', ListHandler),
]
