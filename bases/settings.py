import pymongo
import redis

# 运行方式 debug/release
settings = {
    "run_mode": "debug",
    "secret_key": "R7gKOqXTiti9HuXG",
    "app_jwt_expire": 30 * 24 * 3600,
    "admin_jwt_expire": 24 * 3600,
    "SAVE_URL": "/Users/xxx/Downloads/download",
    "SITE_URL": "http://127.0.0.1/download",
    'redis': {
        "host": "127.0.0.1",
        "port": 6379,
        "password": "123456"
    },
    'mongo': {
        "host": "127.0.0.1",
        "port": 27017,
        "name": "happy-base"
    }
}


# redis 工具类
class RedisTool:
    _instance = None

    @staticmethod
    def get_redis_instance():
        if not RedisTool._instance:
            # 创建连接池
            pool = redis.ConnectionPool(host=settings['redis']['host'], port=settings['redis']['port'],
                                        password=settings['redis']['password'],
                                        decode_responses=True)
            # 创建链接对象
            red = redis.Redis(connection_pool=pool)
            RedisTool._instance = red
        return RedisTool._instance


# mongodb工具类
class MongoTool:
    _instance = None

    @staticmethod
    def get_mongo_instance():
        if not MongoTool._instance:
            mongo_client = pymongo.MongoClient(host=settings['mongo']['host'], port=settings['mongo']['port'])
            MongoTool._instance = mongo_client
        return MongoTool._instance


# redis缓存对象
redisUtil = RedisTool.get_redis_instance()

# mongodb 数据库对象
mongoUtil = MongoTool.get_mongo_instance()
