from tornado.web import url

from core.users.handler_auth import LoginHandler, UserHandler, LogoutHandler, ChangePwdHandler, RefreshLoginHandler

urlpatterns = [
    # 用户认证
    url('/login/', LoginHandler),
    url('/user/', UserHandler),
    url('/logout/', LogoutHandler),
    url('/changePwd/', ChangePwdHandler),
    url('/refreshLogin/', RefreshLoginHandler),
]
