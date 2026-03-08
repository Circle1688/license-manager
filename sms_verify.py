import gradio as gr

import json
import os

from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_tea_util import models as util_models

# from dotenv import load_dotenv
# load_dotenv("app.env")

class SMSVerify:

    @staticmethod
    def create_client():
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=os.getenv("access_key_id"),
            # 必填，您的 AccessKey Secret,
            access_key_secret=os.getenv("access_key_secret")
        )
        # 访问的域名，请参考 https://api.aliyun.com/product/Dypnsapi
        config.endpoint = f'dypnsapi.aliyuncs.com'
        return Dypnsapi20170525Client(config)

    @staticmethod
    def sendSmsVerify(phone_number):
        client = SMSVerify.create_client()
        send_sms_verify_code_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            phone_number=phone_number,
            sign_name='速通互联验证码',
            template_code='100001',
            template_param='{"code":"##code##","min":"5"}'
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.send_sms_verify_code_with_options(send_sms_verify_code_request, runtime)
            print(json.dumps(resp, default=str, indent=2))
            gr.Info("验证码已发送")
            return True
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            gr.Warning(f"发送失败 {error.message}")
            return False

    @staticmethod
    def checkSmsVerifyCode(phone_number, verify_code):
        client = SMSVerify.create_client()
        check_sms_verify_code_request = dypnsapi_20170525_models.CheckSmsVerifyCodeRequest(
            phone_number=phone_number,
            verify_code=verify_code
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            resp = client.check_sms_verify_code_with_options(check_sms_verify_code_request, runtime)
            print(json.dumps(resp, default=str, indent=2))
            return True
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            gr.Warning(f"验证失败 {error.message}")
            return False
