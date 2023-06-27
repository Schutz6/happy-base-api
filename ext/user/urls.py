from tornado.web import url

from ext.user.handler import BindInviteCodeHandler
from ext.user.handler_statistics import StatisticsUserHandler

urlpatterns = [
    # 用户扩展
    url('/user/bindInviteCode/', BindInviteCodeHandler),

    # 用户统计
    url('/user/statistics/', StatisticsUserHandler)
]
