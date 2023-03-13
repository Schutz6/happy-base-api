from bases.settings import redisUtil


# 基础服务器类
class BaseService:
    # redis缓存工具
    redis = redisUtil

    # 应用名称
    appName = "happy:"

    # 用户缓存key
    userKey = appName+"user:"

    # 保存登录令牌
    tokenKey = appName+"token:"

    # 登录错误次数
    loginErrorKey = appName + "login:"

    # 字典缓存Key
    dictKey = appName+"dict:"

    # 系统设置
    settingKey = appName + "setting"


