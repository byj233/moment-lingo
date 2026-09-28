from pydantic import BaseModel


class OCRRequest(BaseModel):
    image_url: str


class ExtensionTranslateRequest(BaseModel):
    content: str


class AIWriteRequest(BaseModel):
    content: str
    corrections: list[dict]
