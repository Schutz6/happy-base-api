import json
import os
import re
import time

from apps.files.models import Files
from bases.decorators import authenticated_async
from config import settings
from bases.handler import BaseHandler
from bases.res import res_func
from bases.utils import show_error_log, get_random, mongo_helper


def get_type(suffix):
    """
    获取文件类型
    :param suffix:
    :return:
    """

    if suffix in ['gif', 'jpg', 'jpeg', 'png', 'webp', 'bmp', 'ico']:
        # 图片
        return 2
    elif suffix in ['mp4', 'm4v', 'mkv', 'webm', 'avi', 'wmv']:
        # 视频
        return 5
    elif suffix in ['mp3', 'amr', 'm4a', 'ogg']:
        # 语音
        return 4
    elif suffix in ['zip', 'rar', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'exe', 'apk']:
        # 文件
        return 3
    else:
        return -1


def get_size(path):
    """
    获取文件大小
    :param path:
    :return:
    """
    size = os.path.getsize(path)
    return format_size(size)


def format_size(_bytes):
    """
    格式化文件大小kb\\m\\g
    :param _bytes:
    :return:
    """
    _bytes = float(_bytes)
    kb = _bytes / 1024
    if kb >= 1024:
        m = kb / 1024
        if m >= 1024:
            g = m / 1024
            return "%.2fG" % g
        else:
            return "%.2fM" % m
    else:
        return "%.2fkb" % kb


class UploadHandler(BaseHandler):
    """
    文件上传
    post -> /file/upload/
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        time_path = time.strftime("%Y%m%d", time.localtime())
        upload_path = os.path.join(os.path.dirname(__file__), settings['SAVE_URL'] + '/files', time_path)
        # 判断文件夹是否存在
        if os.path.isdir(upload_path) is False:
            os.makedirs(upload_path)

        file_metas = self.request.files.get('file', None)
        file_md5 = self.request.arguments.get("md5")

        if file_md5:
            file_md5 = file_md5[0]
            # 检查文件md5值是否已存在
            files_item = await mongo_helper.fetch_one(Files.collection_name, {"md5": str(file_md5, 'utf-8')})
            if files_item is not None:
                # 存在文件，直接返回数据
                data = {
                    "name": files_item['name'],
                    "download_path": settings['SITE_URL'] + files_item['download_path'],
                    "type": files_item['type'],
                    "size": files_item['size']
                }
                res['data'] = data
                self.write(res)
                return

        if not file_metas:
            res['code'] = 10008
            res['message'] = '上传文件为空'
        else:
            try:
                for meta in file_metas:
                    suffix = meta['filename'].split(".")[1].lower()
                    filename = get_random(6) + "." + suffix
                    file_path = os.path.join(upload_path, filename)
                    with open(file_path, 'wb') as up:
                        up.write(meta['body'])
                    # 读取文件信息
                    name = meta['filename']
                    md5 = None
                    if file_md5:
                        md5 = str(file_md5, 'utf-8')
                    download_path = '/files/' + time_path + '/' + filename
                    _type = get_type(suffix)
                    # 判断是否正常的文件类型
                    if _type == -1:
                        res['code'] = 10009
                        res['message'] = '文件类型异常'
                        break
                    size = get_size(file_path)
                    # 入库
                    await mongo_helper.insert_one(Files.collection_name,
                                                  {"_id": await mongo_helper.get_next_id(Files.collection_name),
                                                   "name": name, "md5": md5, "store_path": file_path,
                                                   "download_path": download_path, "type": _type, "size": size,
                                                   "status": 1})

                    # 返回数据
                    data = {
                        "name": name,
                        "download_path": settings['SITE_URL'] + download_path,
                        "type": _type,
                        "size": size
                    }
                    res['data'] = data
                    break

            except Exception as e:
                show_error_log(e)
                res['code'] = 50000
                res['message'] = '操作失败'

        self.write(res)


class HeadUploadHandler(BaseHandler):
    """
        头像上传
        post -> /file/upload/head/
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        time_path = time.strftime("%Y%m%d", time.localtime())
        upload_path = os.path.join(os.path.dirname(__file__), settings['SAVE_URL'] + '/avatars', time_path)
        # 判断文件夹是否存在
        if os.path.isdir(upload_path) is False:
            os.makedirs(upload_path)

        file_metas = self.request.files.get('file', None)
        file_md5 = self.request.arguments.get("md5")
        if file_md5:
            file_md5 = file_md5[0]
            # 检查文件md5值是否已存在
            files_item = await mongo_helper.fetch_one(Files.collection_name, {"md5": str(file_md5, 'utf-8')})
            if files_item is not None:
                # 存在文件，直接返回数据
                data = {
                    "name": files_item['name'],
                    "download_path": settings['SITE_URL'] + files_item['download_path'],
                    "type": files_item['type'],
                    "size": files_item['size']
                }
                res['data'] = data
                self.write(res)
                return

        if not file_metas:
            res['code'] = 10008
            res['message'] = '上传文件为空'
        else:
            try:
                for meta in file_metas:
                    suffix = meta['filename'].split(".")[1].lower()
                    filename = get_random(6) + "." + suffix
                    file_path = os.path.join(upload_path, filename)
                    with open(file_path, 'wb') as up:
                        up.write(meta['body'])
                    # 读取文件信息
                    name = meta['filename']
                    md5 = None
                    if file_md5:
                        md5 = str(file_md5, 'utf-8')
                    download_path = '/avatars/' + time_path + '/' + filename
                    _type = get_type(suffix)
                    # 判断是否正常的文件类型
                    if _type == -1:
                        res['code'] = 10009
                        res['message'] = '文件类型异常'
                        break
                    size = get_size(file_path)
                    # 入库
                    await mongo_helper.insert_one(Files.collection_name,
                                                  {"_id": await mongo_helper.get_next_id(Files.collection_name),
                                                   "name": name, "md5": md5, "store_path": file_path,
                                                   "download_path": download_path, "type": _type, "size": size,
                                                   "status": 2})

                    # 返回数据
                    data = {
                        "name": name,
                        "download_path": settings['SITE_URL'] + download_path,
                        "type": _type,
                        "size": size
                    }
                    res['data'] = data
                    break

            except Exception as e:
                show_error_log(e)
                res['code'] = 50000
                res['message'] = '操作失败'

        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /file/list/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)
        search_key = req_data.get("searchKey")
        _type = req_data.get("type")
        status = req_data.get("status")

        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["name"] = re.compile(search_key)
        if _type is not None:
            query_criteria["type"] = _type
        if status is not None:
            query_criteria["status"] = status

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(Files.collection_name, query_criteria, [("_id", -1)], page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(Files.collection_name, query_criteria)

        results = []
        for item in page_data.get("list", []):
            item["id"] = item["_id"]
            item["download_path"] = settings['SITE_URL'] + item["download_path"]
            results.append(item)

        data = {
            "total": total,
            "size": page_size,
            "current": current_page,
            "results": results
        }

        res['data'] = data
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /file/delete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        if _id is not None:
            # 删除数据
            file = await mongo_helper.fetch_one(Files.collection_name, {"_id": _id})
            if file is not None:
                # 删除记录
                await mongo_helper.delete_one(Files.collection_name, {"_id": _id})
                try:
                    # 删除本地文件
                    os.remove(file["store_path"])
                except Exception as e:
                    show_error_log(e)
        self.write(res)


class BatchDeleteHandler(BaseHandler):
    """
        批量删除
        post -> /file/batchDelete/
    """

    @authenticated_async(['admin', 'super'])
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        ids = req_data.get("ids")

        if ids is not None:
            # 批量删除
            for _id in ids:
                file = await mongo_helper.fetch_one(Files.collection_name, {"_id": int(_id)})
                if file is not None:
                    try:
                        # 删除本地文件
                        os.remove(file["store_path"])
                    except Exception as e:
                        show_error_log(e)
            # 批量删除记录
            await mongo_helper.delete_many(Files.collection_name, {"_id": {"$in": [int(_id) for _id in ids]}})
        self.write(res)
