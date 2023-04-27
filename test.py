import time

from apps.logs.models import Log


# 插入100万日志
# 10000条数据3秒左右
# 100000条数据30秒左右
# 1000000条数据5分钟左右
def init_log():
    print("正在插入")
    data_list = []
    # 开始时间
    start_time = round(time.time() * 1000, 2)
    for i in range(1000000):
        log_db = Log()
        log_db.username = "匿名"
        log_db.method = "GET"
        log_db.uri = "/file/upload/"
        log_db.params = ""
        log_db.ip = "127.0.0.1"
        log_db.times = 10
        data_list.append(log_db.get_add_json())

    # 结束时间
    finish_time1 = round(time.time() * 1000, 2)
    # 访问时间
    times = round(finish_time1 - start_time, 2)
    print(times)
    log_db = Log()
    log_db.insert_many(data_list)
    # 结束时间
    finish_time = round(time.time() * 1000, 2)
    # 访问时间
    times = round(finish_time - start_time, 2)
    print(times)
    print("已完成")


if __name__ == '__main__':
    init_log()
