import logging
import os

import colorlog
from dotenv import load_dotenv

load_dotenv()

logging.getLogger().handlers.clear()

colorlog.basicConfig(
    level=logging.INFO,
    format=(
        "%(log_color)s %(asctime)s - %(name)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(funcName)s  - %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red"
    }
)


class AliYun:
    access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID', '')
    access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET', '')


class Volcengine:
    tts_app_id = os.getenv('VOLCENGINE_TTS_APP_ID', '')
    tts_access_key = os.getenv('VOLCENGINE_TTS_ACCESS_KEY', '')


class Minimax:
    api_key = os.getenv('MINIMAX_API_KEY', '')


class BaseAIConf:
    def __init__(self, base_url: str, api_key: str, provider: str):
        self.base_url = base_url
        self.api_key = api_key
        # 模型供应商
        self.provider = provider


class AIConf:
    volcengine = BaseAIConf(os.getenv('VOLCENGINE_BASE_URL', ''), os.getenv('VOLCENGINE_API_KEY', ''),
        'volcengine')
    bailian = BaseAIConf(os.getenv('BAILIAN_BASE_URL', ''), os.getenv('BAILIAN_API_KEY', ''),
        'bailian')


class RedisConf:
    host = os.getenv('REDIS_HOST', '')
    port = int(os.getenv('REDIS_PORT', 6379))
    username = os.getenv('REDIS_USERNAME', 'default')
    password = os.getenv('REDIS_PASSWORD', '')
    db = int(os.getenv('REDIS_DB', 0))


class DBConf:
    db = os.getenv('DB_NAME', '')
    host = os.getenv('DB_HOST', '')
    port = int(os.getenv('DB_PORT', 3306))
    username = os.getenv('DB_USERNAME', '')
    password = os.getenv('DB_PASSWORD', '')


class Mem0Conf:
    api_key = os.getenv('MEM0_API_KEY', '')
    host = os.getenv('MEM0_HOST', '')


class MeiliConf:
    host = os.getenv('MEILI_HOST', '')
    api_key = os.getenv('MEILI_API_KEY', '')
