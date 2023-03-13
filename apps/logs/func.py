from apps.logs.models import Log
from bases.decorators import run_async


# 异步执行清空日志
@run_async
def clear_log():
    log_db = Log()
    log_db.delete_many({})

