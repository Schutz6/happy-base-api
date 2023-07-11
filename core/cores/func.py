from base.utils import mongo_helper
from config import settings
from core.cores.service import CoreService
from core.users.service import UserService


async def get_obj_info(mid, _id):
    """
    获取对象详情
    :param mid: 模块
    :param _id: ID
    :return: 详情
    """
    info = None
    module = await CoreService.get_module(mid)
    if module is not None:
        if module["cache"] == 0:
            info = await mongo_helper.fetch_one(mid, {"_id": int(_id)})
        else:
            info = await CoreService.get_obj(mid, _id)
        if info is not None:
            replace_img = []
            # 模块检查
            for item2 in module["table_json"]:
                if item2["type"] == 6 or item2["type"] == 8:
                    # 是否需要替换图片
                    replace_img.append(item2["name"])
            # 替换图片地址
            for img in replace_img:
                if info.get(img) is not None:
                    info[img] = info[img].replace("#Image#", settings['SITE_URL'])
    else:
        # 判断是否内置的对象
        if mid == 'User':
            info = await UserService.get_user_by_id(int(_id))
    return info


async def recursion_category_delete(mid, _id):
    """递归删除分类数据"""
    # 判断是否有下级数据
    query = await mongo_helper.fetch_all(mid, {"pid": _id}, [('_id', -1)])
    for item in query:
        # 递归删除
        await recursion_category_delete(mid, item["_id"])
    # 删除上级数据
    await mongo_helper.delete_one(mid, {"_id": _id})

