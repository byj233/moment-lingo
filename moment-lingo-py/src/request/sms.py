from pydantic import BaseModel


class SmsRequest(BaseModel):
    phone: str
    code: str
    exp: int = 5
