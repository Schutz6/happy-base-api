from bases.utils import now_local, format_time


# 测试任务
def task_test(options):
    print('{} [定时任务][task_test]-{}'.format(format_time(now_local(), '%Y/%m/%d %H:%M:%S'), options))
