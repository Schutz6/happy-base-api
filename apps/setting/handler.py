import json

from apps.setting.forms import SettingForm
from apps.setting.service import SettingService
from bases import utils
from bases.decorators import authenticated_async, log_async
from bases.handler import BaseHandler
from bases.res import resFunc


# 保存系统设置
class SaveHandler(BaseHandler):
    '''
        post -> /setting/save/
        payload:
            {
                "content": "设置内容"
            }
    '''

    @authenticated_async
    async def post(self, *args, **kwargs):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = SettingForm.from_json(data)
        content = form.content.data
        current_user = self.current_user
        if 1 in current_user['roles'] or 3 in current_user['roles']:
            # 管理员才能操作
            SettingService.save_system_setting(json.loads(content))
        else:
            res['code'] = 50000
            res['message'] = '权限不够'
        self.write(res)


# 获取网站设置
class InfoHandler(BaseHandler):
    '''
       get -> /setting/getInfo/
    '''

    @log_async
    async def get(self, *args, **kwargs):
        res = resFunc({})
        res["data"] = SettingService.get_system_setting()
        self.write(json.dumps(res, default=utils.json_serial))
