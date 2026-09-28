from pydantic import BaseModel


class EssayCorrectRequest(BaseModel):
    user_id: int
    content: str
