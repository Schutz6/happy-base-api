import json
import re

from base.decorators import authenticated_core
from base.handler import BaseHandler
from base.res import res_func
from base.utils import mongo_helper, now_utc
from config import settings


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
            # 判断是否有唯一字段校验
            if item["unique"]:
                query = await mongo_helper.fetch_one(module["mid"], {item['name']: req_data[item['name']]})
                if query is not None:
                    res['code'] = 10004
                    res['message'] = '已存在'
                    unique = False
                    break
        if unique:
            # 不用校验，直接入库
            _id = await mongo_helper.get_next_id(module["mid"])
            req_data["_id"] = _id
            req_data["add_time"] = now_utc()
            await mongo_helper.insert_one(module["mid"], req_data)
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
                # 唯一字段不能修改
                if item["unique"]:
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

        # 获取模块信息
        module = self.current_user["module"]

        # 需要替换图片地址
        replace_img = []
        # 需要替换对象ID
        object_id = []
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
            if item["type"] == 6 or item["type"] == 8:
                # 需要替换图片地址
                replace_img.append(item["name"])
            elif item["type"] == 9:
                # 为对象ID，获取对象详情
                object_id.append(item["name"])
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
            # 替换对象ID为详情
            for obj in object_id:
                if item.get(obj) is not None:
                    pass
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
            if item["type"] == 6 or item["type"] == 8:
                # 是否需要替换图片
                replace_img.append(item["name"])
            elif item["type"] == 9:
                pass
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
