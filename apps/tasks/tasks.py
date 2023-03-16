from bases.utils import now, format_time, utc_to_local


# 测试任务
def task_test(options):
    print('{} [定时任务][task_test]-{}'.format(format_time(utc_to_local(now()), '%Y/%m/%d %H:%M:%S'), options))
