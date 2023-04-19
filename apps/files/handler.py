import json
import os
import re
import time

from apps.files.forms import FileForm
from apps.files.models import Files
from bases import utils
from bases.decorators import authenticated_async, authenticated_admin_async
from bases.settings import settings
from bases.handler import BaseHandler
from bases.res import resFunc
from bases.utils import show_error_log, get_random


# 获取文件类型
def get_type(suffix):
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


# 获取文件大小
def get_size(path):
    size = os.path.getsize(path)
    return format_size(size)


# 格式化文件大小kb\m\g
def format_size(_bytes):
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


# 文件上传
class UploadHandler(BaseHandler):
    '''
    post -> /file/upload/
    payload:
        {
            "md5": "文件md5值"
            "file": "文件"
        }
    '''

    @authenticated_async
    async def post(self):
        res = resFunc({})
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
            files_db = Files()
            files_item = files_db.find_one({"md5": str(file_md5, 'utf-8')})
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
                    filename = get_random(6)+"."+suffix
                    file_path = os.path.join(upload_path, filename)
                    with open(file_path, 'wb') as up:
                        up.write(meta['body'])
                    # 读取文件信息
                    files = Files()
                    files.name = meta['filename']
                    if file_md5:
                        files.md5 = str(file_md5, 'utf-8')
                    files.store_path = file_path
                    files.download_path = '/files/' + time_path + '/' + filename
                    files.type = get_type(suffix)
                    # 判断是否正常的文件类型
                    if files.type == -1:
                        res['code'] = 10009
                        res['message'] = '文件类型异常'
                        break
                    files.size = get_size(file_path)
                    # 入库
                    files.status = 1
                    await files.insert_one(files.get_add_json())

                    # 返回数据
                    data = {
                        "name": files.name,
                        "download_path": settings['SITE_URL'] + files.download_path,
                        "type": files.type,
                        "size": files.size
                    }
                    res['data'] = data
                    break

            except Exception as e:
                show_error_log(e)
                res['code'] = 50000
                res['message'] = '操作失败'

        self.write(res)


# 头像上传
class HeadUploadHandler(BaseHandler):
    '''
    post -> /file/upload/head/
    payload:
        {
            "md5": "文件md5值"
            "file": "文件"
        }
    '''

    @authenticated_async
    async def post(self):
        res = resFunc({})
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
            files_db = Files()
            files_item = files_db.find_one({"md5": str(file_md5, 'utf-8')})
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
                    files = Files()
                    files.name = meta['filename']
                    if file_md5:
                        files.md5 = str(file_md5, 'utf-8')
                    files.store_path = file_path
                    files.download_path = '/avatars/' + time_path + '/' + filename
                    files.picture = files.download_path
                    files.type = get_type(suffix)
                    # 判断是否正常的文件类型
                    if files.type == -1:
                        res['code'] = 10009
                        res['message'] = '文件类型异常'
                        break
                    files.size = get_size(file_path)
                    # 入库
                    files.status = 2
                    await files.insert_one(files.get_add_json())

                    # 返回数据
                    data = {
                        "name": files.name,
                        "download_path": settings['SITE_URL'] + files.download_path,
                        "type": files.type,
                        "size": files.size
                    }
                    res['data'] = data
                    break

            except Exception as e:
                show_error_log(e)
                res['code'] = 50000
                res['message'] = '操作失败'

        self.write(res)


# 列表
class ListHandler(BaseHandler):
    '''
       post -> /file/list/
       payload:
           {
               "currentPage": 1,
               "pageSize": 10,
               "type": "文件类型",
               "status": "文件状态",
               "searchKey": "关键字",
           }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = FileForm.from_json(data)
        current_page = form.currentPage.data
        page_size = form.pageSize.data
        _type = form.type.data
        status = form.status.data
        search_key = form.searchKey.data
        file_db = Files()
        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_criteria["name"] = re.compile(search_key)
        if _type is not None:
            query_criteria["type"] = _type
        if status is not None:
            query_criteria["status"] = status
        # 查询分页
        query = await file_db.find_page(page_size, current_page, [("_id", -1)], query_criteria)

        # 查询总数
        total = await file_db.query_count(query)
        pages = utils.get_pages(total, page_size)

        results = []
        for item in query:
            item["id"] = item["_id"]
            item["download_path"] = settings['SITE_URL'] + item["download_path"]
            results.append(item)

        data = {
            "total": total,
            "pages": pages,
            "size": page_size,
            "current": current_page,
            "results": results
        }

        res['data'] = data
        self.write(res)


# 删除
class DeleteHandler(BaseHandler):
    '''
        post -> /file/delete/
        payload:
            {
                "id": "编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = FileForm.from_json(data)
        _id = form.id.data
        # 删除数据
        file_db = Files()
        file = await file_db.find_one({"_id": _id})
        if file is not None:
            # 删除记录
            await file_db.delete_one({"_id": _id})
            try:
                # 删除本地文件
                os.remove(file["store_path"])
            except Exception as e:
                show_error_log(e)
        self.write(res)


# 批量删除
class BatchDeleteHandler(BaseHandler):
    '''
       post -> /file/batchDelete/
       payload:
           {
                "ids": "多选ID"
           }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = FileForm.from_json(data)
        ids = form.ids.data
        # 批量删除
        file_db = Files()
        for _id in ids:
            file = await file_db.find_one({"_id": int(_id)})
            if file is not None:
                try:
                    # 删除本地文件
                    os.remove(file["store_path"])
                except Exception as e:
                    show_error_log(e)
        # 批量删除记录
        await file_db.delete_many({"_id": {"$in": [int(_id) for _id in ids]}})
        self.write(res)
