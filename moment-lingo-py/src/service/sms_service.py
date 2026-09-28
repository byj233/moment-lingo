import logging

from src.utils.result import Result
from src.request.sms import SmsRequest
from src.utils.sms import Sms

logger = logging.getLogger(__name__)


async def send_msg(req: SmsRequest) -> Result:
    Sms.send(req.phone, req.code, req.exp)
    return Result.success()
