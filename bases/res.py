'''
返回说明
code
20000 成功
50000 错误
'''


# 返回正常数据
def resFunc(data, code=20000, message="Success"):
    res_model = {
        "data": data,
        "code": code,
        "message": message
    }
    return res_model


# 返回错误数据
def resFailFunc(data, code=50000, message="Failed"):
    res_model = {
        "data": data,
        "code": code,
        "message": message
    }
    return res_model
