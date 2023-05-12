from bases.handler import BaseHandler
from bases.res import resFunc


class CoreHandler(BaseHandler):
    """核心接口"""

    async def post(self):
        res = resFunc({})

        self.write(res)
