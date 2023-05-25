from base.utils import now_utc, mongo_helper


class Files(object):
    """文件库"""

    # 文档名
    collection_name = "Files"

    """数据库字段说明"""
    # 文件名
    name = None
    # 下载地址
    download_path = None
    # 存储地址
    store_path = None
    # 文件类型
    type = 0
    # 文件大小
    size = None
    # 文件md5值
    md5 = None
    # 文件状态 1临时 2永存
    status = 0

    # 格式化json
    @staticmethod
    async def get_json(req_data):
        _id = await mongo_helper.get_next_id(Files.collection_name)
        return {"_id": _id,
                "name": req_data.get("name"),
                "download_path": req_data.get("download_path"),
                "store_path": req_data.get("store_path"),
                "type": req_data.get("type", 0),
                "size": req_data.get("size"),
                "md5": req_data.get("md5"),
                "status": req_data.get("status", 0),
                "add_time": now_utc()}
