from base.utils import mongo_helper
from core.menus.models import Menu


async def recursion_menu_delete(_id):
    """递归删除菜单数据"""
    # 判断是否有下级数据
    query = await mongo_helper.fetch_all(Menu.collection_name, {"pid": _id}, [('_id', -1)])
    for item in query:
        # 递归删除
        await recursion_menu_delete(item["_id"])
    # 删除上级数据
    await mongo_helper.delete_one(Menu.collection_name, {"_id": _id})

