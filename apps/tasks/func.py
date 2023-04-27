from bases.utils import show_error_log


# 执行任务
def run_task(scheduler, task):
    job_id = task["_id"]
    if task['type'] == 2:
        # cron任务类型
        exec_cron = task['exec_cron']
        # 解析指令
        if exec_cron.endswith("D"):
            # 每天xx时间点执行
            try:
                exec_cron = exec_cron.replace("D", "")
                exec_cron = exec_cron.split(":")
                hour = exec_cron[0]
                minute = exec_cron[1]
                scheduler.add_job(task['func'], 'cron', hour=int(hour),
                                  minute=int(minute), id=str(job_id),
                                  args=[task.get("options")])
            except Exception as e:
                show_error_log(e)
    elif task['type'] == 3:
        # 间隔任务类型
        exec_interval = task['exec_interval']
        # 解析指令
        if exec_interval.endswith("S"):
            # 秒指令
            seconds = exec_interval.replace("S", "")
            try:
                seconds = int(seconds)
                scheduler.add_job(task['func'], 'interval', seconds=seconds,
                                  id=str(job_id),
                                  args=[task.get("options")])
            except Exception as e:
                show_error_log(e)
        elif exec_interval.endswith("M"):
            # 分钟指令
            minutes = exec_interval.replace("M", "")
            try:
                minutes = int(minutes)
                scheduler.add_job(task['func'], 'interval', minutes=minutes,
                                  id=str(job_id),
                                  args=[task.get("options")])
            except Exception as e:
                show_error_log(e)
        elif exec_interval.endswith("H"):
            # 小时指令
            hours = exec_interval.replace("H", "")
            try:
                hours = int(hours)
                scheduler.add_job(task['func'], 'interval', hours=hours,
                                  id=str(job_id),
                                  args=[task.get("options")])
            except Exception as e:
                show_error_log(e)
        elif exec_interval.endswith("D"):
            # 天指令
            days = exec_interval.replace("D", "")
            try:
                days = int(days)
                scheduler.add_job(task['func'], 'interval', days=days,
                                  id=str(job_id),
                                  args=[task.get("options")])
            except Exception as e:
                show_error_log(e)
        elif exec_interval.endswith("W"):
            # 周指令
            weeks = exec_interval.replace("W", "")
            try:
                weeks = int(weeks)
                scheduler.add_job(task['func'], 'interval', weeks=weeks,
                                  id=str(job_id),
                                  args=[task.get("options")])
            except Exception as e:
                show_error_log(e)
