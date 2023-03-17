from bases.models import MongoModel
from bases.settings import settings
from bases.utils import now_utc


# 文件信息表
class Files(MongoModel):

    def __init__(self):
        super(Files, self).__init__(settings['mongo']['name'], "Files")

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
    def get_add_json(self):
        return {"_id": self.get_next_id(),
                "name": self.name,
                "download_path": self.download_path,
                "store_path": self.store_path,
                "type": self.type,
                "size": self.size,
                "md5": self.md5,
                "status": self.status,
                "add_time": now_utc()}
