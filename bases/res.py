"""
返回说明
code
20000 成功
50000 错误
"""


def res_func(data, code=20000, message="Success"):
    """返回成功"""
    res_model = {
        "data": data,
        "code": code,
        "message": message
    }
    return res_model


def res_fail_func(data, code=50000, message="Failed"):
    """返回失败"""
    res_model = {
        "data": data,
        "code": code,
        "message": message
    }
    return res_model
