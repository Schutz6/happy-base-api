from core.params.service import ParamService
from base.decorators import log_async
from base.handler import BaseHandler
from base.res import res_func


class GetListHandler(BaseHandler):
    """
        所有列表
        get -> /param/getList/
    """

    @log_async
    async def get(self):
        res = res_func({})
        results = await ParamService.get_params()
        # 转成字典格式
        res['data'] = dict(results)
        self.write(res)
