import json
import re

from base.decorators import authenticated_core
from base.handler import BaseHandler
from base.res import res_func
from base.utils import mongo_helper, now_utc
from config import settings
from core.cores.func import get_obj_info
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
                    add_json[item['name']] = int(add_json[item['name']])
                elif item["type"] == 3:
                    # Float类型转换
                    add_json[item['name']] = float(add_json[item['name']])
                elif item["type"] == 6 or item["type"] == 8:
                    # 图片/富文本 中图片地址转换
                    img = add_json[item['name']]
                    add_json[item['name']] = img.replace(settings['SITE_URL'], "#Image#")
                # 判断是否有唯一字段校验
                if item["unique"]:
                    query = await mongo_helper.fetch_one(module["mid"], {item['name']: add_json[item['name']]})
                    if query is not None:
                        res['code'] = 10004
                        res['message'] = '已存在'
                        unique = False
                        break
        if unique:
            # 不用校验，直接入库
            _id = await mongo_helper.get_next_id(module["mid"])
            add_json["_id"] = _id
            add_json["add_time"] = now_utc()
            await mongo_helper.insert_one(module["mid"], add_json)
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
        # 删除数据
        await mongo_helper.delete_one(module["mid"], {"_id": _id})

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
            # 删除数据
            await mongo_helper.delete_one(module["mid"], {"_id": int(_id)})

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
                    value = req_data.get(item["name"])
                    if value is not None:
                        query_criteria[item["name"]] = value

        # 查询分页数据
        page_data = await mongo_helper.fetch_page_info(module["mid"], query_criteria,
                                                       [("sort", -1), ("_id", -1)], page_size,
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

        # 模块字段检查
        for item in module["table_json"]:
            if item["type"] == 6 or item["type"] == 8:
                # 是否需要替换图片
                replace_img.append(item["name"])
            elif item["type"] == 9:
                # 对象替换成详情
                if item.get("key") is not None:
                    objects.append({"field": item["name"], "mid": item.get("key")})
        query = await mongo_helper.fetch_one(module["mid"], {"_id": int(_id)})
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
