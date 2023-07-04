import smtplib

from email.header import Header
from email.mime.text import MIMEText
from base.utils import show_error_log
from core.params.service import ParamService


async def send_gmail(receiver, title, code):
    """
    发送谷歌邮件
    @param receiver 接受人
    @param title 标题
    @param code 验证码
    """
    try:
        # 获取短信设置
        gmail_user = await ParamService.get_param("gmailUser")
        gmail_password = await ParamService.get_param("gmailPassword")
        gmail_template = await ParamService.get_param("gmailTemplate")
        if gmail_user is not None and gmail_password is not None and gmail_template is not None:
            message = MIMEText(gmail_template["value"].replace("code", code), 'plain', 'utf-8')
            message['From'] = gmail_user["value"]  # 发送者
            message['To'] = receiver  # 接收者

            message['Subject'] = Header(title, 'utf-8')
            smtp = smtplib.SMTP("smtp.gmail.com", 587)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(gmail_user["value"], gmail_password["value"])
            smtp.sendmail(gmail_user["value"], receiver, message.as_string())
            smtp.close()
            return True
        else:
            return False
    except smtplib.SMTPException as e:
        show_error_log(e)
        return False

