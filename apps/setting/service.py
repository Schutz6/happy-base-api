import json

from bases import utils
from bases.service import BaseService


# 系统设置服务类
class SettingService(BaseService):

    # 保存系统设置
    @staticmethod
    def save_system_setting(data):
        SettingService.redis.set(SettingService.settingKey, json.dumps(data, default=utils.json_serial))

    # 获取网站设置
    @staticmethod
    def get_system_setting():
        data = SettingService.redis.get(SettingService.settingKey)
        if data is not None:
            return json.loads(data)
        else:
            return None
