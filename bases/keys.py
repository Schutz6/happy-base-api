class Keys(object):

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

    # 参数设置
    paramsKey = appName + "params:"


""" 单例对象 """
Keys = Keys()
