import json
import logging

from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models

from src import config

logger = logging.getLogger(__name__)


class Sms:
    def __init__(self):
        pass

    @staticmethod
    def _client() -> Dypnsapi20170525Client:
        credential = CredentialClient(config=Config(
            type='access_key',
            access_key_id=config.AliYun.access_key_id,
            access_key_secret=config.AliYun.access_key_secret,
        ))

        return Dypnsapi20170525Client(config=open_api_models.Config(
            credential=credential,
            endpoint=f'dypnsapi.aliyuncs.com'
        ))

    @staticmethod
    def send(phone: str, code: str, exp: int = 5):
        client = Sms._client()
        req = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            template_code='100001',
            sign_name='速通互联验证码',
            template_param=json.dumps({'code': code, 'min': str(exp)}),
            phone_number=phone
        )
        try:
            client.send_sms_verify_code(req)
        except Exception as e:
            logger.error(f'短信服务调用失败 {e}')
            raise e
