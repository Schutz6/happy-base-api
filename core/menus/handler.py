from core.menus.service import MenuService
from base.decorators import authenticated_async
from base.handler import BaseHandler
from base.res import res_func


class GetListHandler(BaseHandler):
    """
        所有列表
        get -> /menu/getList/
    """

    @authenticated_async(None)
    async def get(self):
        res = res_func([])
        current_user = self.current_user
        res['data'] = await MenuService.get_menus(current_user["roles"])
        self.write(res)
