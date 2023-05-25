from core.logs.models import Log
from base.utils import get_add_time, now_utc, mongo_helper


async def clear_log(options):
    """清理日志，只保留7天记录"""
    # 获取7天前的时间，小于这个时间的数据都删掉
    last_time = get_add_time(now_utc(), -int(options))
    await mongo_helper.delete_many(Log.collection_name, {"add_time": {"$lt": last_time}})


