import hashlib
import logging
import random
import time
from decimal import Decimal

from datetime import datetime, date, timedelta
from urllib.parse import urlparse


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, date):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, Decimal):
        return str(Decimal(obj).quantize(Decimal('0.00')))
    raise TypeError("Type {}s not serializable".format(obj))


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


# 获取当前时间
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 获取上n分钟
def now_last_minute(minute):
    # 当前时间
    old_time = datetime.now()
    # 减去n分钟
    add_time = timedelta(minutes=minute)
    # 增加后时间
    return (old_time + add_time).strftime("%Y-%m-%d %H:%M:%S")


# 获取当前日期
def now_day():
    return datetime.now().strftime("%Y-%m-%d")


# 获取当前时间目录
def now_path():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


# 获取唯一的账单编号
def get_order_no():
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + str(time.time()).replace('.', '')[-7:]
    return order_no


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


# 获取增加天数时间
def get_add_time(_time, days):
    # 原时间
    old_time = datetime.strptime(_time, "%Y-%m-%d %H:%M:%S")
    # 增加时间
    add_time = timedelta(days=days)
    # 增加后时间
    return (old_time + add_time).strftime("%Y-%m-%d %H:%M:%S")


# 比较时间的大小
def time_cmp(first_time, second_time):
    _strftime = datetime.strptime(first_time, "%Y-%m-%d %H:%M:%S")
    strftime2 = datetime.strptime(second_time, "%Y-%m-%d %H:%M:%S")
    return _strftime > strftime2


# 替换域名地址
def replace_url(domain, url):
    # 将url中原域名去掉
    url_obj = urlparse(url)
    # 拼接上新的域名
    return domain+url_obj.path
