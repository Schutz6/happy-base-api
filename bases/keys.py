class Keys(object):

    # 应用名称
    appName = "happy:"
    # 用户
    userKey = appName+"user:"
    # 登录令牌
    tokenKey = appName+"token:"
    # 错误次数
    loginErrorKey = appName + "login:"
    # 菜单
    menusKey = appName + "menus:"
    # 字典
    dictKey = appName+"dict:"
    # 参数
    paramsKey = appName + "params:"
    # IP黑名单
    ipBlacklistKey = appName + "ipBlacklist:"
    # IP限流
    ipLimitKey = appName + "ipLimit:"
    # API限流
    apiLimitKey = appName + "apiLimit"
    # 代码
    codeKey = appName + "code:"


""" 单例对象 """
Keys = Keys()
