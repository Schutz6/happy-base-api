import json

from apps.dicts.forms import DictTypeForm, DictValueForm
from apps.dicts.models import DictType, DictValue
from apps.dicts.service import DictService
from bases.handler import BaseHandler
from bases.decorators import log_async, authenticated_admin_async
from bases.res import resFunc
from bases.settings import settings


class ListDictTypeHandler(BaseHandler):
    '''
        获取字典类型列表
        get -> /dict/typeList/
    '''

    @authenticated_admin_async
    async def get(self):
        res = resFunc([])
        dictType_db = DictType()
        # 查询所有
        query = dictType_db.find_all({"_id": {"$ne": "sequence_id"}})
        # 排序
        dictTypes = dictType_db.query_sort(query, [("_id", -1)])
        results = []
        for dictType in dictTypes:
            dictType["id"] = dictType["_id"]
            # 查询子集
            dictType["children"] = DictService.get_dict_list(dictType["_id"])

            results.append(dictType)

        res['data'] = results

        self.write(res)


class AddDictTypeHandler(BaseHandler):
    '''
        新增字典类型
        post -> /dict/typeAdd/
        payload:
            {
                "id": "编号",
                "name": "角色",
                "describe": "描述"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = DictTypeForm.from_json(data)
        _id = form.id.data
        name = form.name.data
        describe = form.describe.data
        dictType = DictType()
        if _id is not None:
            # 编辑
            dictType.update_one({"_id": _id}, {"$set": {"name": name, "describe": describe}})
        else:
            # 新增
            dictType.name = name
            dictType.describe = describe
            dictType.insert_one(dictType.get_add_json())
        res['message'] = '保存成功'

        self.write(res)


class DeleteDictTypeHandler(BaseHandler):
    '''
        删除字典类型
        post -> /dict/typeDelete/
        payload:
            {
                "id":"编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = DictTypeForm.from_json(data)
        # 删除类型
        dictType = DictType()
        dictType.id = form.id.data
        dictType.delete_one({"_id": dictType.id})

        # 删除值
        dictValue = DictValue()
        dictValue.delete_many({"dict_tid": dictType.id})

        # 删除缓存
        DictService.delete_cache(dictType.id)

        res['message'] = '删除成功'
        self.write(res)


class ListDictValueHandler(BaseHandler):
    '''
        获取字典值列表
        post -> /dict/valueList/
        payload:
            {
                "dict_tid": "字典类型编号"
            }
    '''

    @log_async
    async def post(self):
        res = resFunc([])
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = DictValueForm.from_json(data)

        res['data'] = DictService.get_dict_list(form.dict_tid.data)

        self.write(res)


class AddDictValueHandler(BaseHandler):
    '''
        新增字典值
        post -> /dict/valueAdd/
        payload:
            {
                "id": "编号",
                "dict_tid": "字典类型编号",
                "dict_name": "字典名称",
                "dict_value": "字典值",
                "sort": "自定义排序"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = DictValueForm.from_json(data)
        _id = form.id.data
        dict_name = form.dict_name.data
        dict_value = form.dict_value.data
        sort = form.sort.data
        dict_tid = form.dict_tid.data
        dictValue = DictValue()
        if _id is not None:
            # 编辑
            dictValue.update_one({"_id": _id},
                                 {"$set": {"dict_name": dict_name, "dict_value": dict_value, "sort": sort}})
        else:
            dictValue.dict_tid = dict_tid
            dictValue.dict_name = dict_name
            dictValue.dict_value = dict_value
            dictValue.sort = sort
            dictValue.insert_one(dictValue.get_add_json())
            res['message'] = '添加成功'
        # 删除缓存
        DictService.delete_cache(dict_tid)

        self.write(res)


class DeleteDictValueHandler(BaseHandler):
    '''
        删除字典值
        post -> /dict/valueDelete/
        payload:
            {
                "id":"编号",
                "dict_tid": "字典类型编号"
            }
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc({})
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = DictValueForm.from_json(data)
        dictValue = DictValue()
        dictValue.id = form.id.data
        dictValue.delete_one({"_id": dictValue.id})
        res['message'] = '删除成功'
        # 删除缓存
        DictService.delete_cache(form.dict_tid.data)

        self.write(res)


class GetDictListHandler(BaseHandler):
    '''
        获取字典列表
        post -> /dict/getList/
        payload:
            {
                "name":"字典名称"
            }
    '''

    @log_async
    async def post(self):
        res = resFunc([])
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = DictTypeForm.from_json(data)
        name = form.name.data

        dict_type_db = DictType()
        dict_type = dict_type_db.find_one({"name": name})
        if dict_type is not None:
            results = []
            query = DictService.get_dict_list(dict_type["_id"])
            if name == "Avatar":
                # 头像处理
                for item in query:
                    item["dict_value"] = settings['SITE_URL'] + item["dict_value"]
                    results.append({"text": item["dict_name"], "value": item["dict_value"]})
            else:
                for item in query:
                    results.append({"text": item["dict_name"], "value": item["dict_value"]})
            res['data'] = results
        self.write(res)
