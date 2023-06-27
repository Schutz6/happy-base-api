import json

from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func, res_fail_func
from base.utils import mongo_helper
from core.users.models import User
from core.users.service import UserService


class BindInviteCodeHandler(BaseHandler):
    """
        绑定邀请码
        post -> /user/bindInviteCode/
        payload:
          {
              "invite_code": "邀请码"
          }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_fail_func(None)
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        invite_code = req_data.get("invite_code")

        if invite_code is not None:
            current_user = self.current_user
            invite_code = int(invite_code)
            if current_user["_id"] != invite_code:
                # 查询邀请码是否存在
                invite_user = await UserService.get_user_by_id(invite_code)
                if invite_user is not None:
                    # 绑定上级用户
                    await mongo_helper.update_one(User.collection_name, {"_id": current_user["_id"]},
                                                  {"$set": {"pid": invite_user["_id"]}})
                    # 删除缓存
                    UserService.delete_cache(current_user["_id"])
                    res = res_func({})
        self.write(res)
