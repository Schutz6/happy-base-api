from tornado.web import url

from ext.user.handler import BindInviteCodeHandler, RealnameHandler, CertifiedHandler, UserBalanceHandler
from ext.user.handler_agent import InviteListHandler, AgentTeamHandler, AgentIncomeListHandler
from ext.user.handler_recharge import UserCertifiedRechargeHandler
from ext.user.handler_statistics import StatisticsUserHandler
from ext.user.handler_withdraw import UserWithdrawHandler, UserCertifiedWithdrawHandler

urlpatterns = [
    # 用户扩展
    url('/user/bindInviteCode/', BindInviteCodeHandler),
    url('/user/realname/', RealnameHandler),
    url('/user/certified/', CertifiedHandler),
    url('/user/balance/', UserBalanceHandler),

    # 用户代理
    url('/agent/inviteList/', InviteListHandler),
    url('/agent/team/', AgentTeamHandler),
    url('/agent/incomeList/', AgentIncomeListHandler),

    # 用户充值
    url('/user/certifiedRecharge/', UserCertifiedRechargeHandler),

    # 用户提现
    url('/user/withdraw/', UserWithdrawHandler),
    url('/user/certifiedWithdraw/', UserCertifiedWithdrawHandler),

    # 用户统计
    url('/user/statistics/', StatisticsUserHandler)
]
