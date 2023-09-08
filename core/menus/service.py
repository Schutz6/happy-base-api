import json

from base.keys import Keys
from base.utils import redis_helper, mongo_helper


class MenuService(object):
    """菜单服务类"""

    @staticmethod
    def remove_menus():
        """删除菜单缓存"""
        redis_helper.redis.delete(Keys.menusKey)

    @staticmethod
    async def get_menus(roles):
        """获取菜单列表"""
        results = []
        menus = redis_helper.redis.get(Keys.menusKey)
        if menus is None:
            # 查询一级菜单
            query_one = await mongo_helper.fetch_all("Menu", {"pid": 0, "status": "1"}, [("sort", -1), ("_id", -1)])
            for one in query_one:
                # 查询二级菜单
                query_two = await mongo_helper.fetch_all("Menu", {"pid": one["_id"], "status": "1"},
                                                         [("sort", -1), ("_id", -1)])
                children2 = []
                for two in query_two:
                    item2 = {"text": two["name"], "value": two["url"], "icon": two.get("icon"),
                             "roles": two.get("roles", []), "projects": two.get("projects", [])}
                    # 查询三级菜单
                    query_three = await mongo_helper.fetch_all("Menu", {"pid": two["_id"], "status": "1"},
                                                               [("sort", -1), ("_id", -1)])
                    children3 = []
                    for three in query_three:
                        children3.append({"text": three["name"], "value": three["url"], "icon": three.get("icon"),
                                          "roles": three.get("roles", []), "projects": three.get("projects", [])})
                    if len(children3) > 0:
                        item2["children"] = children3
                    children2.append(item2)
                results.append(
                    {"text": one["name"], "value": one["url"], "icon": one.get("icon"), "roles": one.get("roles", []),
                     "projects": one.get("projects", []),
                     "children": children2})
                if len(results) > 0:
                    # 存储
                    redis_helper.redis.set(Keys.menusKey, json.dumps(results))
        else:
            results = json.loads(menus)
        # 筛选菜单
        results = MenuService.filter_menu(roles, results)
        return results

    @staticmethod
    def filter_menu(roles, results):
        """
        根据角色筛选菜单
        """
        new_results = []
        # 循环第一层
        for item in results:
            if MenuService.check_role(roles, item["roles"]):
                children2 = []
                # 循环第二层
                for item2 in item.get("children", []):
                    if MenuService.check_role(roles, item2["roles"]):
                        children3 = []
                        # 循环第三层
                        for item3 in item2.get("children", []):
                            if MenuService.check_role(roles, item3["roles"]):
                                children3.append(
                                    {"text": item3["text"], "value": item3["value"], "icon": item3.get("icon"),
                                     "projects": item3.get("projects", [])})
                        children2.append({"text": item2["text"], "value": item2["value"], "icon": item2.get("icon"),
                                          "projects": item2.get("projects", []),
                                          "children": children3})
                new_results.append(
                    {"text": item["text"], "value": item["value"], "icon": item.get("icon"),
                     "projects": item.get("projects", []), "children": children2})
        return new_results

    @staticmethod
    def check_role(self_roles, roles):
        """
        检查角色权限
        """
        for role in self_roles:
            if role in roles:
                return True
        return False
