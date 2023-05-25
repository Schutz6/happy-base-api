from base.utils import mongo_helper
from config import settings
from core.cores.service import CoreService


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
        info = await mongo_helper.fetch_one(mid, {"_id": int(_id)})
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
    return info
