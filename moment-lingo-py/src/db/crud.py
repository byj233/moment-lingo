from src.db import orm
from src.utils.sql import BaseCRUD


class EssayCRUD(BaseCRUD[orm.Essay]):
    pass


class VoiceCRUD(BaseCRUD[orm.Voice]):
    pass
