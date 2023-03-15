import json

from apps.dicts.forms import DictTypeForm, DictValueForm
from apps.dicts.models import DictType, DictValue
from apps.dicts.service import DictService
from bases.handler import BaseHandler
from bases.decorators import log_async, authenticated_admin_async
from bases.res import resFunc
from bases import utils
from bases.settings import settings


# 获取字典类型列表
class ListDictTypeHandler(BaseHandler):
    '''
        post -> /dictType/list/
    '''

    @authenticated_admin_async
    async def post(self):
        res = resFunc([])
        dictType_db = DictType()
        # 查询所有
        query = await dictType_db.find_all({"_id": {"$ne": "sequence_id"}})
        # 排序
        dictTypes = await dictType_db.query_sort(query, [("_id", -1), ("add_time", -1)])
        results = []
        for dictType in dictTypes:
            dictType["id"] = dictType["_id"]
            results.append(dictType)

        res['data'] = results

        self.write(json.dumps(res, default=utils.json_serial))


# 新增字典类型
class AddDictTypeHandler(BaseHandler):
    '''
        post -> /dictType/add/
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
        dictType = DictType()
        if _id is not None:
            # 编辑
            await dictType.update_one({"_id": _id}, {"$set": {"name": name}})
        else:
            # 新增
            dictType.name = name
            dictType.describe = form.describe.data
            await dictType.insert_one(dictType.get_add_json())
        res['message'] = '保存成功'

        self.write(res)


# 删除字典类型
class DeleteDictTypeHandler(BaseHandler):
    '''
        post -> /dictType/delete/
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
        await dictType.delete_one({"_id": dictType.id})

        # 删除值
        dictValue = DictValue()
        await dictValue.delete_many({"dict_tid": dictType.id})

        # 删除缓存
        DictService.delete_cache(dictType.id)

        res['message'] = '删除成功'
        self.write(res)


# 获取字典值列表
class ListDictValueHandler(BaseHandler):
    '''
        post -> /dictValue/list/
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

        res['data'] = await DictService.get_dict_list(form.dict_tid.data)

        self.write(json.dumps(res, default=utils.json_serial))


# 新增字典值
class AddDictValueHandler(BaseHandler):
    '''
        post -> /dictValue/add/
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
            await dictValue.update_one({"_id": _id},
                                 {"$set": {"dict_name": dict_name, "dict_value": dict_value, "sort": sort}})
        else:
            dictValue.dict_tid = dict_tid
            dictValue.dict_name = dict_name
            dictValue.dict_value = dict_value
            dictValue.sort = sort
            await dictValue.insert_one(dictValue.get_add_json())
            res['message'] = '添加成功'
        # 删除缓存
        DictService.delete_cache(dict_tid)

        self.write(res)


# 删除字典值
class DeleteDictValueHandler(BaseHandler):
    '''
        post -> /dictValue/delete/
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
        await dictValue.delete_one({"_id": dictValue.id})
        res['message'] = '删除成功'
        # 删除缓存
        DictService.delete_cache(form.dict_tid.data)

        self.write(res)


# 获取字典列表
class GetDictListHandler(BaseHandler):
    '''
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
        dict_type = await dict_type_db.find_one({"name": name})
        if dict_type is not None:
            results = []
            query = await DictService.get_dict_list(dict_type["_id"])
            if name == "Avatar":
                # 头像处理
                for item in query:
                    item["dict_value"] = settings['SITE_URL'] + item["dict_value"]
                    results.append(item)
            else:
                results = query
            res['data'] = results
        self.write(json.dumps(res, default=utils.json_serial))
