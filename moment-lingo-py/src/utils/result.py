from typing import Any

from pydantic import BaseModel, model_serializer

from src.utils.common import timestamp, to_lower_camel

MAX_SAFE_INTEGER = 2 ** 53 - 1
MIN_SAFE_INTEGER = -(2 ** 53 - 1)


class Result(BaseModel):
    code: int
    msg: str
    data: Any | None = None
    timestamp: int = timestamp()

    @staticmethod
    def _convert_large_int(data: Any) -> Any:
        """递归将超出 JS 安全整数范围的 int 转为 str"""
        if isinstance(data, bool):
            # bool 是 int 子类，必须先判断
            return data
        elif isinstance(data, int):
            if data > MAX_SAFE_INTEGER or data < MIN_SAFE_INTEGER:
                return str(data)
            return data
        elif isinstance(data, dict):
            return {k: Result._convert_large_int(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [Result._convert_large_int(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(Result._convert_large_int(item) for item in data)
        elif isinstance(data, BaseModel):
            # 先转为 dict 再递归处理
            return Result._convert_large_int(data.model_dump())
        else:
            return data

    @model_serializer
    def serialize_model(self) -> dict:
        """序列化时自动转换所有超范围的 int"""
        return {
            'code': self.code,
            'msg': self.msg,
            'data': to_lower_camel(Result._convert_large_int(self.data)),
            'timestamp': Result._convert_large_int(self.timestamp)
        }

    @staticmethod
    def success(data: Any | None = None, *, msg: str = '成功'):
        if not isinstance(data, (list, dict, str, int, float, bool, type(None), BaseModel)):
            data = str(data)
        return Result(code=200, msg=msg, data=data)

    @staticmethod
    def error(msg: str, *, code: int = 500, data: Any | None = None):
        if not isinstance(data, (list, dict, str, int, float, bool, type(None), BaseModel)):
            data = str(data)
        return Result(code=code, msg=msg, data=data)
