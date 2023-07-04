import json

from base.aliyun import send_aliyun_mobile, send_aliyun_g_mobile
from base.decorators import log_async, authenticated_async
from base.gmail import send_gmail
from base.handler import BaseHandler
from base.res import res_func
from base.utils import get_random_num, mongo_helper, get_md5
from core.params.service import ParamService
from core.users.service import UserService


class SendEmailHandler(BaseHandler):
    """
    发送邮件验证码
    post -> /user/sendEmail/
    payload:
        {
            "email": "邮箱"
        }
    """

    @log_async
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        email = req_data.get("email")
        # 获取邮箱验证码
        save_code = UserService.get_sms_code(email)
        if save_code is not None:
            res['code'] = 10019
            res['message'] = '发送验证码间隔不能小于5分钟'
        else:
            # 创建一个验证码
            code = get_random_num(6)
            # 发送邮件
            flag = send_gmail(email, "验证码", code)
            if flag:
                # 发送成功之后，保存到redis
                UserService.save_sms_code(email, code)
                res['code'] = 20000
                res['message'] = '验证码发送成功'
            else:
                res['code'] = 10021
                res['message'] = '验证码发送失败'
        self.write(res)


class SendMobileHandler(BaseHandler):
    """
    发送手机验证码
    post -> /user/sendMobile/
    payload:
        {
            "type": "类型 1注册 2登录 3找回密码",
            "area": "86",
            "mobile": "手机号"
        }
    """

    @log_async
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        _type = req_data.get("type")
        area = req_data.get("area")
        mobile = req_data.get("mobile")
        # 判断类型
        if _type == 2 or _type == 3:
            # 登录、找回密码，判断账号是否存在
            user = await mongo_helper.fetch_one("User", {"area": area, "mobile": mobile})
            if user is None:
                res['code'] = 10025
                res['message'] = '账号还未注册，请先注册'
                self.write(res)
                return
        if _type == 1:
            # 注册之后，不用重新发送
            user = await mongo_helper.fetch_one("User", {"area": area, "mobile": mobile})
            if user is not None:
                res['code'] = 10026
                res['message'] = '账号已注册，请直接登录'
                self.write(res)
                return
        # 获取手机验证码
        save_code = UserService.get_sms_code(area + mobile)
        if save_code is not None:
            res['code'] = 10019
            res['message'] = '发送验证码间隔不能小于5分钟'
        else:
            # 创建一个验证码
            code = get_random_num(6)
            if area == '86':
                # 阿里国内短信
                flag = send_aliyun_mobile(area + mobile, code)
            else:
                # 阿里国际短信
                flag = send_aliyun_g_mobile(area + mobile, code)
            if flag:
                # 发送成功之后，保存到redis
                UserService.save_sms_code(area + mobile, code)
                res['code'] = 20000
                res['message'] = '验证码发送成功'
            else:
                res['code'] = 10021
                res['message'] = '验证码发送失败'
        self.write(res)


class BindMobileHandler(BaseHandler):
    """
    绑定手机号
    post -> /user/bindMobile/
    payload:
       {
            "area": "区号",
            "mobile": "新手机号",
            "code": "验证码"
       }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        area = req_data.get("area")
        mobile = req_data.get("mobile")
        code = req_data.get("code")

        current_user = self.current_user

        # 获取邮箱验证码
        save_code = UserService.get_sms_code(area + mobile)
        if save_code is None:
            # 使用通用验证码
            default_code = await ParamService.get_param("defaultCode")
            if default_code is not None:
                save_code = default_code["value"]

        if save_code != code:
            res['code'] = 10003
            res['message'] = '验证码错误'
        else:
            # 判断手机号是否已存在
            user = await mongo_helper.fetch_one("User", {"area": area, "mobile": mobile})
            if user is not None:
                res['code'] = 10004
                res['message'] = '该账号已存在'
                self.write(res)
                return
            # 修改用户手机号
            await mongo_helper.update_one("User", {"_id": current_user["_id"]},
                                          {"$set": {"area": area, "mobile": mobile}})
            # 删除缓存
            UserService.delete_cache(current_user["_id"])
        self.write(res)


class BindEmailHandler(BaseHandler):
    """
    绑定用户邮箱
    post -> /user/bindEmail/
    payload:
       {
            "email": "邮箱",
            "code": "验证码"
       }
    """

    @authenticated_async(None)
    async def post(self):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        email = req_data.get("email")
        code = req_data.get("code")

        current_user = self.current_user

        # 获取邮箱验证码
        save_code = UserService.get_sms_code(email)
        if save_code is None:
            # 使用通用验证码
            default_code = await ParamService.get_param("defaultCode")
            if default_code is not None:
                save_code = default_code["value"]

        if save_code != code:
            res['code'] = 10003
            res['message'] = '验证码错误'
        else:
            user = await mongo_helper.fetch_one("User", {"email": email})
            if user is not None:
                res['code'] = 10004
                res['message'] = '该账号已存在'
                self.write(res)
                return
            # 修改用户邮箱
            await mongo_helper.update_one("User", {"_id": current_user["_id"]}, {"$set": {"email": email}})
            # 删除缓存
            UserService.delete_cache(current_user["_id"])
        self.write(res)


class ReplacePasswordHandler(BaseHandler):
    """
    忘记密码，更新新密码
    post -> /user/replacePassword/
    payload:
        {
            "area": "区号",
            "mobile": "新手机号",
            "email": "邮箱",
            "code": "验证码"
            "password": "密码"
        }
    """

    @log_async
    async def post(self, *args, **kwargs):
        res = res_func({})
        data = self.request.body.decode('utf-8')
        req_data = json.loads(data)
        area = req_data.get("area")
        mobile = req_data.get("mobile")
        email = req_data.get("email")
        code = req_data.get("code")
        password = req_data.get("password")

        # 判断是手机/邮箱更新新密码
        if mobile is not None:
            # 手机找回
            save_code = UserService.get_sms_code(area + mobile)
            if save_code is None:
                # 使用通用验证码
                default_code = await ParamService.get_param("defaultCode")
                if default_code is not None:
                    save_code = default_code["value"]
            if save_code != code:
                res['code'] = 10003
                res['message'] = '验证码错误'
            else:
                user = await mongo_helper.fetch_one("User", {"area": area, "mobile": mobile})
                if user is not None:
                    await mongo_helper.update_one("User", {"_id": user["_id"]},
                                                  {"$set": {"password": get_md5(password)}})
                    # 删除缓存
                    UserService.delete_cache(user["_id"])
        else:
            # 邮箱找回
            save_code = UserService.get_sms_code(email)
            if save_code is None:
                # 使用通用验证码
                default_code = await ParamService.get_param("defaultCode")
                if default_code is not None:
                    save_code = default_code["value"]
            if save_code != code:
                res['code'] = 10003
                res['message'] = '验证码错误'
            else:
                user = await mongo_helper.fetch_one("User", {"email": email})
                if user is not None:
                    await mongo_helper.update_one("User", {"_id": user["_id"]},
                                                  {"$set": {"password": get_md5(password)}})
                    # 删除缓存
                    UserService.delete_cache(user["_id"])
        self.write(res)
