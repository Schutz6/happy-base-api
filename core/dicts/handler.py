import json

from core.dicts.service import DictService
from base.handler import BaseHandler
from base.decorators import log_async
from base.res import res_func
from config import settings


class GetDictListHandler(BaseHandler):
    """
        获取字典列表
        post -> /dict/getList/
    """

    @log_async
    async def post(self):
        res = res_func([])
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        type_name = req_data.get("type_name")

        results = []
        query = await DictService.get_dict_list(type_name)
        if type_name == "Avatar":
            # 头像处理
            for item in query:
                item["dict_value"] = settings['SITE_URL'] + item["value"]
                results.append({"text": item["text"], "value": item["value"]})
        else:
            for item in query:
                results.append({"text": item["text"], "value": item["value"]})
        res['data'] = results

        self.write(res)
