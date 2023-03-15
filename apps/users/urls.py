from tornado.web import url

from apps.users.handler import AddHandler, Deletehandler, UpdateHandler, ListHandler
from apps.users.handler_auth import LoginHandler, UserHandler, LogoutHandler, ChangePwdHandler, RefreshLoginHandler

urlpatterns = [
    # 用户认证
    url('/login/', LoginHandler),
    url('/user/', UserHandler),
    url('/logout/', LogoutHandler),
    url('/changePwd/', ChangePwdHandler),
    url('/refreshLogin/', RefreshLoginHandler),

    # 用户模块
    url('/user/add/', AddHandler),
    url('/user/delete/', Deletehandler),
    url('/user/update/', UpdateHandler),
    url('/user/list/', ListHandler)

]