from tornado.web import url

from ext.user.handler import BindInviteCodeHandler, RealnameHandler, CertifiedHandler
from ext.user.handler_statistics import StatisticsUserHandler

urlpatterns = [
    # 用户扩展
    url('/user/bindInviteCode/', BindInviteCodeHandler),
    url('/user/realname/', RealnameHandler),
    url('/user/certified/', CertifiedHandler),

    # 用户统计
    url('/user/statistics/', StatisticsUserHandler)
]
