import hashlib
import logging
import random

from datetime import datetime, timedelta
from urllib.parse import urlparse


def get_pages(total, pageSize):
    '''
    获取分页信息
    :param count: 总数
    :return: 总页数
    '''
    pages = 1
    if total > pageSize:
        pages = total // pageSize
        if total % pageSize:
            pages += 1
    return pages


# 获取md5值
def get_md5(value):
    m = hashlib.md5()
    m.update(value.encode("utf8"))
    return m.hexdigest()


# 获取随机头像
def get_random_head():
    return '/users/default.png'


# 打印错误日志
def show_error_log(msg):
    logging.error(msg)


# 格式化时间
def format_time(_time, fmt):
    return datetime.fromtimestamp(_time/1000).strftime(fmt)


# 获取UTC时间戳
def now_utc():
    return int(datetime.utcnow().timestamp() * 1000)


# 获取本地时间戳
def now_local():
    return int(datetime.now().timestamp() * 1000)


# 本地时间转UTC时间戳
def local_to_utc(_time):
    return int(datetime.utcfromtimestamp(_time/1000).timestamp() * 1000)


# UTC时间转本地时间戳
def utc_to_local(_utctime):
    local_tm = datetime.fromtimestamp(0)
    utc_tm = datetime.utcfromtimestamp(0)
    offset = local_tm - utc_tm
    return int((datetime.fromtimestamp(_utctime/1000) + offset).timestamp() * 1000)


# 获取上n分钟（UTC）
def now_last_minute(minute):
    # 当前时间
    old_time = datetime.now()
    # 减去n分钟
    add_time = timedelta(minutes=minute)
    # 增加后时间
    return local_to_utc((old_time + add_time).timestamp() * 1000)


# 获取增加天数时间
def get_add_time(_utctime, days):
    # 原时间(utc转本地时间)
    old_time = datetime.fromtimestamp(utc_to_local(_utctime)/1000)
    # 增加时间
    add_time = timedelta(days=days)
    # 增加后时间
    return local_to_utc((old_time + add_time).timestamp() * 1000)


# 比较时间的大小
def time_cmp(first_time, second_time):
    return first_time > second_time


# 获取唯一的账单编号
def get_order_no(module):
    return module


# 获取随机数(数字+字母)
def get_random(num):
    seeds = '123456789abcdefghjkmnopqrstuvwxy'
    code = []
    for i in range(num):
        code.append(random.choices(seeds)[0])
    return ''.join(code)


# 获取随机数（数字）
def get_random_num(num):
    seeds = '123456789'
    code = []
    for i in range(num):
        code.append(random.choices(seeds)[0])
    return ''.join(code)


# 替换域名地址
def replace_url(domain, url):
    # 将url中原域名去掉
    url_obj = urlparse(url)
    # 拼接上新的域名
    return domain + url_obj.path
