from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from base.utils import show_error_log
from core.params.service import ParamService


async def send_aliyun_mobile(mobile, code):
    """
    发送国内手机短信
    @param mobile 手机号
    @param code 验证码
    """
    try:
        # 获取短信设置
        aliyun_id = await ParamService.get_param("aliyun_accesskey_id")
        aliyun_secret = await ParamService.get_param("aliyun_accesskey_secret")
        aliyun_sign = await ParamService.get_param("aliyun_sign")
        aliyun_template = await ParamService.get_param("aliyun_template")
        if aliyun_id is not None and aliyun_secret is not None and aliyun_sign is not None and aliyun_template is not None:
            client = AcsClient(aliyun_id["value"], aliyun_secret["value"], 'cn-hangzhou')
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('dysmsapi.aliyuncs.com')
            request.set_method('POST')
            request.set_version('2017-05-25')
            request.set_action_name('SendSms')
            request.add_query_param('RegionId', "cn-hangzhou")
            request.add_query_param('PhoneNumbers', mobile)
            request.add_query_param('SignName', aliyun_sign["value"])
            request.add_query_param('TemplateCode', aliyun_template["value"])
            request.add_query_param('TemplateParam', "{'code':'"+code+"'}")
            response = client.do_action_with_exception(request)
            show_error_log(str(response, encoding='utf-8'))
            return True
        else:
            return False
    except Exception as e:
        show_error_log(e)
        return False


async def send_aliyun_g_mobile(mobile, code):
    """
    发送国际手机短信
    @param mobile 手机号
    @param code 验证码
    """
    try:
        # 获取短信设置
        aliyun_id = await ParamService.get_param("aliyun_accesskey_id")
        aliyun_secret = await ParamService.get_param("aliyun_accesskey_secret")
        aliyun_sms_content = await ParamService.get_param("aliyun_sms_content")
        if aliyun_id is not None and aliyun_secret is not None and aliyun_sms_content is not None:
            client = AcsClient(aliyun_id["value"], aliyun_secret["value"], 'ap-southeast-1')
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('dysmsapi.ap-southeast-1.aliyuncs.com')
            request.set_method('POST')
            request.set_version('2018-05-01')
            request.set_action_name('SendMessageToGlobe')
            request.add_query_param('To', mobile)
            request.add_query_param('Message', aliyun_sms_content["value"].replace("code", code))
            response = client.do_action_with_exception(request)
            show_error_log(str(response, encoding='utf-8'))
            return True
        else:
            return False
    except Exception as e:
        show_error_log(e)
        return False
