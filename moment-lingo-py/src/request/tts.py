from pydantic import BaseModel


class TtsRequest(BaseModel):
    content: str
    model: str
    voice_key: str
    rate: float = 1.0
