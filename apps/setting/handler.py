import json

from apps.setting.forms import SettingForm
from apps.setting.service import SettingService
from bases import utils
from bases.decorators import log_async, authenticated_admin_async
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

    @authenticated_admin_async
    async def post(self, *args, **kwargs):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = SettingForm.from_json(data)
        content = form.content.data
        SettingService.save_system_setting(json.loads(content))
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
