from bases.utils import mongo_helper, now_utc


class Backup(object):
    """数据库备份"""

    # 文档名
    collection_name = "Backup"

    """数据库字段说明"""
    # 备份目录
    directory = None
    # 备份时间
    add_time = None

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Backup.collection_name)
        return {"_id": _id,
                "directory": req_data.get("directory"),
                "add_time": now_utc()}
