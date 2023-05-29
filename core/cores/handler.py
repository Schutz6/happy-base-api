import json
import os
import re
import time

from openpyxl.reader.excel import load_workbook

from base.decorators import authenticated_core
from base.handler import BaseHandler
from base.res import res_func, res_fail_func
from base.utils import mongo_helper, now_utc, get_random
from base.xlsx import save_to_excel
from config import settings
from core.cores.func import get_obj_info, recursion_category_delete
from core.cores.service import CoreService


class AddHandler(BaseHandler):
    """
        添加
        post -> /core/add/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)

        # 校验唯一性
        unique = True

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        add_json = {}
        # 判断哪些字段需要添加
        for item in module["table_json"]:
            value = req_data.get(item["name"])
            if value is not None:
                # 加入字段
                add_json[item["name"]] = value

                if item["type"] == 2 or item["type"] == 9:
                    # Int/Object类型转换
                    add_json[item['name']] = int(add_json.get(item['name']))
                elif item["type"] == 3:
                    # Float类型转换
                    add_json[item['name']] = float(add_json.get(item['name']))
                elif item["type"] == 6 or item["type"] == 8:
                    # 图片/富文本 中图片地址转换
                    img = add_json.get(item['name'])
                    add_json[item['name']] = img.replace(settings['SITE_URL'], "#Image#")
                # 判断是否有唯一字段校验
                if item["unique"]:
                    query = await mongo_helper.fetch_one(module["mid"], {item['name']: add_json.get(item['name'])})
                    if query is not None:
                        res['code'] = 10004
                        res['message'] = '已存在'
                        unique = False
                        break
            else:
                # 使用默认值
                if item.get("default") is not None:
                    add_json[item["name"]] = item["default"]
        if unique:
            # 不用校验，直接入库
            _id = await mongo_helper.get_next_id(module["mid"])
            add_json["_id"] = _id
            add_json["add_time"] = now_utc()
            await mongo_helper.insert_one(module["mid"], add_json)
        self.write(res)


class RecursionDeleteHandler(BaseHandler):
    """
        递归删除
        post -> /core/recursionDelete/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        if _id is not None:
            _id = int(_id)
            # 递归删除数据
            await recursion_category_delete(module["mid"], _id)
            # 删除缓存
            CoreService.remove_category(module["mid"])
        else:
            res = res_fail_func(None)
        self.write(res)


class DeleteHandler(BaseHandler):
    """
        删除
        post -> /core/delete/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        if _id is not None:
            _id = int(_id)
            # 删除数据
            await mongo_helper.delete_one(module["mid"], {"_id": _id})
            if module["cache"] == 1:
                # 删除缓存
                await CoreService.remove_obj(module["mid"], _id)
        else:
            res = res_fail_func(None)
        self.write(res)


class BatchDeleteHandler(BaseHandler):
    """
        批量删除
        post -> /core/batchDelete/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        ids = req_data.get("ids")

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        for _id in ids:
            _id = int(_id)
            # 删除数据
            await mongo_helper.delete_one(module["mid"], {"_id": _id})
            if module["cache"] == 1:
                # 删除缓存
                await CoreService.remove_obj(module["mid"], _id)

        self.write(res)


class UpdateHandler(BaseHandler):
    """
        修改
        post -> /core/update/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        _id = req_data.get("id")

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        if _id is not None:
            _id = int(_id)
            update_json = {}
            # 判断哪些字典需要修改
            for item in module["table_json"]:
                value = req_data.get(item["name"])
                if value is not None:
                    # 唯一字段/Object字段不能修改
                    if item["unique"] or item["type"] == 9:
                        # 处理下一个字段
                        continue
                    # 处理其他字段
                    update_json[item["name"]] = value

                    if item["type"] == 2:
                        # Int类型转换
                        update_json[item['name']] = int(update_json[item['name']])
                    elif item["type"] == 3:
                        # Float类型转换
                        update_json[item['name']] = float(update_json[item['name']])
                    elif item["type"] == 6 or item["type"] == 8:
                        # 图片/富文本 中图片地址转换
                        img = update_json[item['name']]
                        update_json[item['name']] = img.replace(settings['SITE_URL'], "#Image#")
            # 修改数据
            await mongo_helper.update_one(module["mid"], {"_id": _id}, {"$set": update_json})
            if module["cache"] == 1:
                # 删除缓存
                await CoreService.remove_obj(module["mid"], _id)
        else:
            res = res_fail_func(None)
        self.write(res)


class BatchUpdateHandler(BaseHandler):
    """
        批量修改
        post -> /core/batchUpdate/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)
        ids = req_data.get("ids")

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        for _id in ids:
            _id = int(_id)
            update_json = {}
            # 判断哪些字典需要修改
            for item in module["table_json"]:
                value = req_data.get(item["name"])
                if value is not None:
                    update_json[item["name"]] = value
            # 修改数据
            await mongo_helper.update_one(module["mid"], {"_id": _id}, {"$set": update_json})
            if module["cache"] == 1:
                # 删除缓存
                await CoreService.remove_obj(module["mid"], _id)
        self.write(res)


class ListHandler(BaseHandler):
    """
        列表
        post -> /core/list/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        current_page = req_data.get("currentPage", 1)
        page_size = req_data.get("pageSize", 10)
        search_key = req_data.get("searchKey")
        sort_field = req_data.get("sortField", "_id")
        sort_order = req_data.get("sortOrder", "descending")
        uid = req_data.get("uid")

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        # 需要替换图片地址
        replace_img = []
        # 需要替换对象ID
        objects = []

        # 字符串查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_list = []
            for item in module["table_json"]:
                # 是否是查询条件
                if item["query"]:
                    if item["type"] == 1 or item["type"] == 7:
                        query_list.append({item["name"]: re.compile(search_key)})
            if len(query_list) > 0:
                query_criteria["$or"] = query_list
        # 查询自己的数据
        if uid is not None:
            query_criteria["uid"] = int(uid)
        # 字典查询条件
        for item in module["table_json"]:
            if item["type"] == 6 or item["type"] == 8:
                # 需要替换图片地址
                replace_img.append(item["name"])
            elif item["type"] == 9:
                # 对象替换成详情
                if item.get("key") is not None:
                    objects.append({"field": item["name"], "mid": item.get("key")})
            # 是否是查询条件
            if item["query"]:
                if item["type"] == 5:
                    # 查询字典
                    value = req_data.get(item["name"])
                    if value is not None:
                        query_criteria[item["name"]] = value
                elif item["type"] == 10:
                    # 查询分类
                    value = req_data.get(item["name"])
                    if value is not None and len(value) > 0:
                        query_criteria[item["name"]] = value

        # 排序条件
        if sort_field == "_id":
            sort_data = [(sort_field, -1 if sort_order == 'descending' else 1)]
        else:
            sort_data = [(sort_field, -1 if sort_order == 'descending' else 1), ("_id", -1)]

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(module["mid"], query_criteria,
                                                       sort_data, page_size,
                                                       current_page)
        # 查询总数
        total = await mongo_helper.fetch_count_info(module["mid"], query_criteria)

        results = []
        for item in page_data.get("list", []):
            item["id"] = item["_id"]
            item.pop("_id")
            # 替换图片地址
            for img in replace_img:
                if item.get(img) is not None:
                    item[img] = item[img].replace("#Image#", settings['SITE_URL'])
            # 查询对象详情
            for obj in objects:
                info = await get_obj_info(obj["mid"], item[obj["field"]])
                if info is not None:
                    # 匹配字段
                    for table in module["table_json"]:
                        if table["name"].find(obj["mid"]) > -1:
                            # 匹配上字段，给该字段赋值
                            item[table["name"]] = info[table["name"].replace(obj["mid"] + ".", "")]
            results.append(item)
        data = {
            "total": total,
            "size": page_size,
            "current": current_page,
            "results": results
        }

        res['data'] = data
        self.write(res)


class GetListHandler(BaseHandler):
    """
        所有列表
        post -> /core/getList/
    """

    @authenticated_core
    async def post(self):
        res = res_func([])
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        uid = req_data.get("uid")

        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        # 需要替换图片地址
        replace_img = []
        # 需要替换对象ID
        objects = []

        # 模块字段检查
        for item in module["table_json"]:
            if item["type"] == 6 or item["type"] == 8:
                # 是否需要替换图片
                replace_img.append(item["name"])
            elif item["type"] == 9:
                # 对象替换成详情
                if item.get("key") is not None:
                    objects.append({"field": item["name"], "mid": item.get("key")})
        # 查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        # 查询自己的数据
        if uid is not None:
            query_criteria["uid"] = int(uid)
        query = await mongo_helper.fetch_all(module["mid"], query_criteria, [("sort", -1), ("_id", -1)])
        results = []
        for item in query:
            item["id"] = item["_id"]
            item.pop("_id")
            # 替换图片地址
            for img in replace_img:
                if item.get(img) is not None:
                    item[img] = item[img].replace("#Image#", settings['SITE_URL'])
            # 查询对象详情
            for obj in objects:
                info = await get_obj_info(obj["mid"], item[obj["field"]])
                if info is not None:
                    # 匹配字段
                    for table in module["table_json"]:
                        if table["name"].find(obj["mid"]) > -1:
                            # 匹配上字段，给该字段赋值
                            item[table["name"]] = info[table["name"].replace(obj["mid"] + ".", "")]
            results.append(item)
        res['data'] = results
        self.write(res)


class GetCategoryHandler(BaseHandler):
    """
        获取分类列表
        post -> /core/getCategory/
    """

    @authenticated_core
    async def post(self):
        res = res_func([])

        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        # 需要替换图片地址
        replace_img = []

        # 模块字段检查
        for item in module["table_json"]:
            if item["type"] == 6:
                # 是否需要替换图片
                replace_img.append(item["name"])
        # 获取分类列表
        query = await CoreService.get_category(module["mid"])
        results = []
        for item in query:
            # 替换图片地址
            for img in replace_img:
                if item.get(img) is not None:
                    item[img] = item[img].replace("#Image#", settings['SITE_URL'])
            # 查询分类下使用数量

            results.append(item)
        res['data'] = results
        self.write(res)


class GetInfoHandler(BaseHandler):
    """
        获取详情
        post -> /core/getInfo/
    """

    @authenticated_core
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _id = req_data.get("id")

        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        # 需要替换图片地址
        replace_img = []
        # 需要替换对象ID
        objects = []

        if _id is not None:
            _id = int(_id)
            # 模块字段检查
            for item in module["table_json"]:
                if item["type"] == 6 or item["type"] == 8:
                    # 是否需要替换图片
                    replace_img.append(item["name"])
                elif item["type"] == 9:
                    # 对象替换成详情
                    if item.get("key") is not None:
                        objects.append({"field": item["name"], "mid": item.get("key")})
            if module["cache"] == 1:
                query = await CoreService.get_obj(module["mid"], _id)
            else:
                query = await mongo_helper.fetch_one(module["mid"], {"_id": _id})
            if query is not None:
                query["id"] = query["_id"]
                query.pop("_id")
                # 替换图片地址
                for img in replace_img:
                    if query.get(img) is not None:
                        query[img] = query[img].replace("#Image#", settings['SITE_URL'])
                # 查询对象详情
                for obj in objects:
                    info = await get_obj_info(obj["mid"], query[obj["field"]])
                    if info is not None:
                        # 匹配字段
                        for table in module["table_json"]:
                            if table["name"].find(obj["mid"]) > -1:
                                # 匹配上字段，给该字段赋值
                                query[table["name"]] = info[table["name"].replace(obj["mid"] + ".", "")]
                res['data'] = query
        self.write(res)


class ImportDataHandler(BaseHandler):
    """
        导入数据
        post -> /core/importData/
    """

    @authenticated_core
    async def post(self):
        res = res_func(None)

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        # 需要导入的字段
        fields = []

        # 字典查询条件
        for item in module["table_json"]:
            if item["type"] in [1, 2, 3, 5, 6, 7, 8]:
                fields.append(item["name"])

        time_path = time.strftime("%Y%m%d", time.localtime())
        upload_path = os.path.join(os.path.dirname(__file__), settings['SAVE_URL'] + '/files', time_path)
        # 判断文件夹是否存在
        if os.path.isdir(upload_path) is False:
            os.makedirs(upload_path)

        file_metas = self.request.files.get('file', None)
        if not file_metas:
            res['code'] = 50000
            res['message'] = '上传文件为空'
        else:
            for meta in file_metas:
                suffix = meta['filename'].split(".")[1].lower()
                filename = get_random(6) + "." + suffix
                file_path = os.path.join(upload_path, filename)
                with open(file_path, 'wb') as up:
                    up.write(meta['body'])
                wb = load_workbook(file_path)
                # 获得sheet对象
                ws = wb.active
                # 读取数据
                index = 2

                while index <= ws.max_row:
                    column_index = 1
                    add_json = {}
                    for key in fields:
                        value = ws.cell(row=index, column=column_index).value
                        add_json[key] = value
                        column_index += 1
                    # 加入数据库
                    _id = await mongo_helper.get_next_id(module["mid"])
                    add_json["_id"] = _id
                    add_json["add_time"] = now_utc()
                    await mongo_helper.insert_one(module["mid"], add_json)
                    index = index + 1
                res['message'] = '导入成功'
        self.write(res)


class ExportDataHandler(BaseHandler):
    """
        导出数据
        post -> /core/exportData/
    """

    @authenticated_core
    async def post(self):
        res = res_func(None)
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        search_key = req_data.get("searchKey")
        sort_field = req_data.get("sortField", "_id")
        sort_order = req_data.get("sortOrder", "descending")
        uid = req_data.get("uid")

        # 当前用户信息
        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        # 需要替换图片地址
        replace_img = []
        # 需要替换对象ID
        objects = []

        # 字符串查询条件
        query_criteria = {"_id": {"$ne": "sequence_id"}}
        if search_key is not None:
            query_list = []
            for item in module["table_json"]:
                # 是否是查询条件
                if item["query"]:
                    if item["type"] == 1 or item["type"] == 7:
                        query_list.append({item["name"]: re.compile(search_key)})
            if len(query_list) > 0:
                query_criteria["$or"] = query_list
        # 查询自己的数据
        if uid is not None:
            query_criteria["uid"] = int(uid)

        # 头部数据
        head_row = []
        # 需要导出的字段
        fields = []

        # 字典查询条件
        for item in module["table_json"]:
            if item["type"] in [1, 2, 3, 5, 6, 7, 8]:
                # 记录导出头部
                head_row.append(item["remarks"])
                fields.append(item["name"])

            if item["type"] == 6 or item["type"] == 8:
                # 需要替换图片地址
                replace_img.append(item["name"])
            elif item["type"] == 9:
                # 对象替换成详情
                if item.get("key") is not None:
                    objects.append({"field": item["name"], "mid": item.get("key")})
            # 是否是查询条件
            if item["query"]:
                if item["type"] == 5:
                    # 查询字典
                    value = req_data.get(item["name"])
                    if value is not None:
                        query_criteria[item["name"]] = value
                elif item["type"] == 10:
                    # 查询分类
                    value = req_data.get(item["name"])
                    if value is not None and len(value) > 0:
                        query_criteria[item["name"]] = value

        # 排序条件
        if sort_field == "_id":
            sort_data = [(sort_field, -1 if sort_order == 'descending' else 1)]
        else:
            sort_data = [(sort_field, -1 if sort_order == 'descending' else 1), ("_id", -1)]

        # 查询数据
        query = await mongo_helper.fetch_all(module["mid"], query_criteria,  sort_data)

        results = []
        for item in query:
            item.pop("_id")
            item.pop("add_time")
            # 替换图片地址
            for img in replace_img:
                if item.get(img) is not None:
                    item[img] = item[img].replace("#Image#", settings['SITE_URL'])
            # 查询对象详情
            for obj in objects:
                info = await get_obj_info(obj["mid"], item[obj["field"]])
                if info is not None:
                    # 匹配字段
                    for table in module["table_json"]:
                        if table["name"].find(obj["mid"]) > -1:
                            # 匹配上字段，给该字段赋值
                            item[table["name"]] = info[table["name"].replace(obj["mid"] + ".", "")]
            obj = []
            for key in fields:
                obj.append(item[key])
            results.append(obj)

        # 保存文件位置
        save_excel_name = str(now_utc()) + ".xlsx"
        res["data"] = save_to_excel(results, head_row, save_excel_name)
        self.write(res)
