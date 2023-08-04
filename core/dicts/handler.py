import json

from core.dicts.service import DictService
from base.handler import BaseHandler
from base.decorators import authenticated_async
from base.res import res_func
from config import settings


class GetDictListHandler(BaseHandler):
    """
        获取字典列表
        post -> /dict/getList/
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func([])
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        type_name = req_data.get("type_name")

        current_user = self.current_user

        results = []

        query = await DictService.get_dict_list(type_name)
        if type_name == "Role":
            # 如果是获取角色列表，必须按照用户权限获取
            flag = False
            for item in query:
                if current_user.get("roles") is not None:
                    if current_user["roles"][0] == item["value"]:
                        flag = True
                    if flag:
                        results.append({"text": item["text"], "value": item["value"]})
                else:
                    results.append({"text": item["text"], "value": item["value"]})
        elif type_name == "Avatar":
            # 头像处理
            for item in query:
                item["dict_value"] = settings['SITE_URL'] + item["value"]
                results.append({"text": item["text"], "value": item["value"]})
        else:
            for item in query:
                results.append({"text": item["text"], "value": item["value"]})
        res['data'] = results

        self.write(res)
