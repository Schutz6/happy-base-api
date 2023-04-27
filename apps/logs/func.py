from apps.logs.models import Log
from bases.decorators import run_async


@run_async
def async_clear_log():
    log_db = Log()
    log_db.delete_many({})
