import json

from apps.menus.models import Menu
from bases.keys import Keys
from bases.utils import redis_helper, mongo_helper


class MenuService(object):
    """菜单服务类"""

    @staticmethod
    def remove_menus():
        """删除菜单缓存"""
        items = redis_helper.redis.keys(pattern=Keys.menusKey + '*')
        if len(items) > 0:
            redis_helper.redis.delete(*items)

    @staticmethod
    async def get_menus(roles):
        """获取菜单列表"""
        results = []
        menus = redis_helper.redis.get(Keys.menusKey + '-'.join(roles))
        if menus is None:
            # 查询一级菜单
            query_one = await mongo_helper.fetch_all(Menu.collection_name,
                                                     {"pid": 0, "status": 1, "roles": {"$in": roles}},
                                                     [("sort", -1), ("_id", -1)])
            for one in query_one:
                # 查询二级菜单
                query_two = await mongo_helper.fetch_all(Menu.collection_name, {"pid": one["_id"], "status": 1,
                                                                                "roles": {"$in": roles}},
                                                         [("sort", -1), ("_id", -1)])
                children = []
                for two in query_two:
                    children.append({"text": two["name"], "value": two["url"], "icon": two.get("icon")})
                results.append(
                    {"text": one["name"], "value": one["url"], "icon": one.get("icon"), "children": children})
                if len(results) > 0:
                    # 存储
                    redis_helper.redis.set(Keys.menusKey + '-'.join(roles), json.dumps(results))
        else:
            results = json.loads(menus)
        return results
