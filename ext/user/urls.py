from tornado.web import url

from ext.user.handler_statistics import StatisticsUserHandler

urlpatterns = [

    # 用户统计
    url('/user/statistics/', StatisticsUserHandler)

]
