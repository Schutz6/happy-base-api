from base.utils import now_local, format_time


async def test(options):
    """测试任务"""
    print('{} [定时任务][task_test]-{}'.format(format_time(now_local(), '%Y/%m/%d %H:%M:%S'), options))
