from pymongo import ReturnDocument

from bases.settings import mongoUtil


# MongoDB基础实体
class MongoModel(object):
    """初始化"""

    _id = 0
    add_time = None
    update_time = None

    def __init__(self, db_name, collection):
        self.client = mongoUtil
        self.collection = self.client[db_name][collection]

    def get_next_id(self):
        next_id = MongoBaseHandle.get_next_id(self.collection)
        return next_id

    async def insert_one(self, data):
        res = await MongoBaseHandle.insert_one(self.collection, data)
        return res

    async def insert_many(self, data_list):
        res = await MongoBaseHandle.insert_many(self.collection, data_list)
        return res

    async def update_one(self, data, data_set):
        res = await MongoBaseHandle.update_one(self.collection, data, data_set)
        return res

    async def update_many(self, data, data_set):
        res = await MongoBaseHandle.update_many(self.collection, data, data_set)
        return res

    async def find_one(self, data, data_field={}):
        res = await MongoBaseHandle.find_one(self.collection, data, data_field)
        return res

    async def find_many(self, data, data_field={}):
        """ 有多个键值的话就是 AND 的关系"""
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_all(self, data={}, data_field={}):
        """select * from table"""
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_in(self, field, item_list, data_field={}):
        """SELECT * FROM inventory WHERE status in ("A", "D")"""
        data = dict()
        data[field] = {"$in": item_list}
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_or(self, data_list, data_field={}):
        """db.inventory.find(
        {"$or": [{"status": "A"}, {"qty": {"$lt": 30}}]})

        SELECT * FROM inventory WHERE status = "A" OR qty < 30
        """
        data = dict()
        data["$or"] = data_list
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_between(self, field, value1, value2, data_field={}):
        """获取俩个值中间的数据"""
        data = dict()
        data[field] = {"$gt": value1, "$lt": value2}
        # data[field] = {"$gte": value1, "$lte": value2} # <>   <= >=
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_more(self, field, value, data_field={}):
        data = dict()
        data[field] = {"$gt": value}
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_less(self, field, value, data_field={}):
        data = dict()
        data[field] = {"$lt": value}
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_like(self, field, value, data_field={}):
        """ where key like "%audio% """
        data = dict()
        data[field] = {'$regex': '.*' + value + '.*'}
        res = await MongoBaseHandle.find_many(self.collection, data, data_field)
        return res

    async def find_page(self, page_size, current_page, sort_data, data, data_field={}):
        res = await MongoBaseHandle.find_page(self.collection, page_size, current_page, sort_data, data, data_field)
        return res

    async def query_limit(self, query, num):
        """db.collection.find(<query>).limit(<number>) 获取指定数据"""
        res = query.limit(num)
        return res

    async def query_count(self, query):
        res = query.count()
        return res

    async def query_skip(self, query, num):
        res = query.skip(num)
        return res

    async def query_sort(self, query, data):
        """db.orders.find().sort( [(amount, -1)] ) 根据amount 降序排列"""
        res = query.sort(data)
        return res

    async def delete_one(self, data):
        """ 删除单行数据 如果有多个 则删除第一个"""
        res = await MongoBaseHandle.delete_one(self.collection, data)
        return res

    async def delete_many(self, data):
        """ 删除查到的多个数据 data 是一个字典 """
        res = await MongoBaseHandle.delete_many(self.collection, data)
        return res

    async def aggregate(self, data):
        res = await MongoBaseHandle.aggregate(self.collection, data)
        return res


# MongoDB操作
class MongoBaseHandle(object):

    @staticmethod
    def get_next_id(collection):
        """获取自增ID"""
        res = collection.find_one_and_update({"_id": "sequence_id"}, {"$inc": {"seq": 1}},
                                             projection={'seq': True, '_id': False},
                                             return_document=ReturnDocument.AFTER)
        if res is not None:
            next_id = res["seq"]
        else:
            collection.insert_one({"_id": "sequence_id", "seq": 1})
            next_id = 1
        return next_id

    @staticmethod
    async def insert_one(collection, data):
        """直接使用insert() 可以插入一条和插入多条 不推荐 明确区分比较好"""
        res = collection.insert_one(data)
        return res.inserted_id

    @staticmethod
    async def insert_many(collection, data_list):
        res = collection.insert_many(data_list)
        return res.inserted_ids

    @staticmethod
    async def find_one(collection, data, data_field={}):
        if len(data_field):
            res = collection.find_one(data, data_field)
        else:
            res = collection.find_one(data)
        return res

    @staticmethod
    async def find_many(collection, data, data_field={}):
        """ data_field 是指输出 操作者需要的字段"""
        if len(data_field):
            res = collection.find(data, data_field)
        else:
            res = collection.find(data)
        return res

    @staticmethod
    async def find_page(collection, page_size, current_page, sort_data, data, data_field={}):
        if len(data_field):
            res = collection.find(data, data_field).sort(sort_data).limit(page_size).skip(
                page_size * (current_page - 1))
        else:
            res = collection.find(data).sort(sort_data).limit(page_size).skip(page_size * (current_page - 1))
        return res

    @staticmethod
    async def update_one(collection, data_condition, data_set):
        """修改一条数据"""
        res = collection.update_one(data_condition, data_set)
        return res

    @staticmethod
    async def update_many(collection, data_condition, data_set):
        """ 修改多条数据 """
        res = collection.update_many(data_condition, data_set)
        return res

    @staticmethod
    async def replace_one(collection, data_condition, data_set):
        """ 完全替换掉 这一条数据， 只是 _id 不变"""
        res = collection.replace_one(data_condition, data_set)
        return res

    @staticmethod
    async def delete_many(collection, data):
        res = collection.delete_many(data)
        return res

    @staticmethod
    async def delete_one(collection, data):
        res = collection.delete_one(data)
        return res

    @staticmethod
    async def aggregate(collection, data):
        res = collection.aggregate(data)
        return res
