import json
import re

from bases.decorators import authenticated_core
from bases.handler import BaseHandler
from bases.res import res_func, res_fail_func
from bases.utils import mongo_helper, now_utc
from config import settings
from cores.service import CoreService


class AddHandler(BaseHandler):
    """
        添加
        post -> /core/add/
    """

    @authenticated_core
    async def post(self):
        res = res_fail_func(None)
        data = self.request.body.decode("utf-8")
        req_data = json.loads(data)

        # 获取模块信息
        module = self.current_user["module"]
        for item in module["table_json"]:
            if item["type"] == 2:
                # Int类型转换
                req_data[item['name']] = int(req_data[item['name']])
            elif item["type"] == 3:
                # Float类型转换
                req_data[item['name']] = float(req_data[item['name']])
            elif item["type"] == 6 or item["type"] == 8:
                # 图片/富文本 中图片地址转换
                img = req_data[item['name']]
                req_data[item['name']] = img.replace(settings['SITE_URL'], "#Image#")
        _id = await mongo_helper.get_next_id(module["mid"])
        req_data["_id"] = _id
        req_data["add_time"] = now_utc()
        await mongo_helper.insert_one(module["mid"], req_data)
        res = res_func({})

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

        # 获取模块信息
        module = self.current_user["module"]
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

        # 获取模块信息
        module = self.current_user["module"]

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

        # 获取模块信息
        module = self.current_user["module"]

        update_json = {}
        # 判断哪些字典需要修改
        for item in module["table_json"]:
            value = req_data.get(item["name"])
            if value is not None:
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

        # 获取模块信息
        module = self.current_user["module"]

        # 需要替换图片地址
        replace_img = []
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
        # 字典查询条件
        for item in module["table_json"]:
            # 是否需要替换图片
            if item["type"] == 6 or item["type"] == 8:
                replace_img.append(item["name"])
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
    async def get(self):
        res = res_func([])

        current_user = self.current_user
        # 获取模块信息
        module = current_user["module"]

        # 需要替换图片地址
        replace_img = []
        for item in module["table_json"]:
            # 是否需要替换图片
            if item["type"] == 6 or item["type"] == 8:
                replace_img.append(item["name"])
        query = await mongo_helper.fetch_all(module["mid"], {"_id": {"$ne": "sequence_id"}},
                                             [("sort", -1), ("_id", -1)])
        results = []
        for item in query:
            item["id"] = item["_id"]
            item.pop("_id")
            # 替换图片地址
            for img in replace_img:
                if item.get(img) is not None:
                    item[img] = item[img].replace("#Image#", settings['SITE_URL'])
            results.append(item)
        res['data'] = results
        self.write(res)
