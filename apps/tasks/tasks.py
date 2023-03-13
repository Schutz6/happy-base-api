from bases.utils import now


# 测试任务
def task_test(options):
    print('{} [定时任务][task_test]-{}'.format(now(), options))
