from __future__ import annotations

import abc
from enum import Enum
from typing import Any, Generic, Type, TypeVar, get_origin, get_args, cast

from pydantic import BaseModel
from sqlmodel import SQLModel, Session, asc, desc, func, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T", bound=SQLModel)


class ConditionOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GE = "ge"
    LE = "le"
    IN = "in"
    NOT_IN = "not in"
    LIKE = "like"
    CONTAINS = "contains"

    @classmethod
    def from_str(cls, op_str: str) -> "ConditionOperator":
        """
        根据字符串解析对应的操作符枚举。
        :param op_str: 操作符字符串
        :return: 对应的 ConditionOperator 枚举实例
        :raises ValueError: 如果操作符无效
        """
        op_str_lower = op_str.strip().lower()
        for member in cls:
            if member.value == op_str_lower:
                return member
        raise ValueError(f"无效的操作符 '{op_str}'，支持的操作符：{[m.value for m in cls]}")


class BaseCondition(abc.ABC):
    def __and__(self, other: "BaseCondition") -> "LogicalCondition":
        """
        重载 & 运算符，用于组合两个条件为 AND 逻辑条件。
        :param other: 另一个基础条件
        :return: AND 逻辑条件实例
        """
        return LogicalCondition("and", [self, other])

    def __or__(self, other: "BaseCondition") -> "LogicalCondition":
        """
        重载 | 运算符，用于组合两个条件为 OR 逻辑条件。
        :param other: 另一个基础条件
        :return: OR 逻辑条件实例
        """
        return LogicalCondition("or", [self, other])


class LogicalCondition(BaseCondition):
    logical_op: str
    conditions: list[BaseCondition]

    def __init__(self, op: str, conditions: list[BaseCondition]):
        """
        初始化逻辑条件。
        :param op: 逻辑操作符（'and' 或 'or'）
        :param conditions: 包含的子条件列表
        """
        self.logical_op = op
        self.conditions = conditions

    def __and__(self, other: "BaseCondition") -> "LogicalCondition":
        """
        重载 & 运算符，支持链式组合 AND 逻辑条件。
        :param other: 要追加的条件
        :return: 新的或合并后的逻辑条件
        """
        if self.logical_op == "and":
            return LogicalCondition("and", self.conditions + [other])
        return super().__and__(other)

    def __or__(self, other: "BaseCondition") -> "LogicalCondition":
        """
        重载 | 运算符，支持链式组合 OR 逻辑条件。
        :param other: 要追加的条件
        :return: 新的或合并后的逻辑条件
        """
        if self.logical_op == "or":
            return LogicalCondition("or", self.conditions + [other])
        return super().__or__(other)


class FieldCondition(BaseCondition):
    field: Any | None
    value: Any
    op: ConditionOperator

    def __init__(self, value: Any, op: str | ConditionOperator = ConditionOperator.EQ, field: Any | None = None):
        """
        初始化字段条件。
        :param value: 比较的值
        :param op: 操作符，默认为等值匹配(EQ)
        :param field: 指定的字段对象或字段名
        """
        self.value = value
        self.op = ConditionOperator.from_str(op)
        self.field = field


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

    @classmethod
    def from_str(cls, dir_str: str) -> "OrderDirection":
        """
        根据字符串解析对应的排序方向枚举。
        :param dir_str: 排序方向字符串
        :return: 对应的 OrderDirection 枚举实例
        :raises ValueError: 如果方向无效
        """
        dir_str_lower = dir_str.strip().lower()
        for member in cls:
            if member.value == dir_str_lower:
                return member
        raise ValueError(f"无效的排序方向 '{dir_str}'，支持的方向：{[m.value for m in cls]}")


class OrderCondition:
    field: Any
    direction: OrderDirection

    def __init__(self, field: Any, direction: str | OrderDirection = OrderDirection.ASC):
        """
        初始化排序条件。
        :param field: 排序依据的字段
        :param direction: 排序方向，默认为升序(ASC)
        """
        self.field = field
        self.direction = OrderDirection.from_str(direction)


class BaseCRUDMeta(abc.ABCMeta):
    def __init__(cls, name, bases, attrs):
        """
        元类初始化，自动提取并校验泛型类中的 model_cls 属性。
        :param name: 类名
        :param bases: 基类元组
        :param attrs: 类的属性字典
        """
        super().__init__(name, bases, attrs)
        if name == "BaseCRUD":
            return

        # 跳过通过 Generic 产生的中间泛型类
        if cls._is_generic_alias(bases):
            return

        # 尝试从泛型参数中提取 model_cls
        if "model_cls" not in attrs:
            orig_bases = getattr(cls, "__orig_bases__", tuple())
            for base in orig_bases:
                origin = get_origin(base)
                if origin is not None and isinstance(origin, type) and issubclass(origin, BaseCRUD):
                    args = get_args(base)
                    if args:
                        arg = args[0]
                        if isinstance(arg, TypeVar):
                            # 参数仍为 TypeVar，说明这是个派生的中间泛型类，比如 class MiddleCrud(BaseCrud[T])
                            return
                        elif isinstance(arg, type):
                            cls.model_cls = arg
                            return

        if not hasattr(cls, "model_cls"):
            raise ValueError(f"类 {name} 必须定义 'model_cls' 属性或者在继承时提供泛型参数")

    @staticmethod
    def _is_generic_alias(bases) -> bool:
        """检查是否是 Generic 参数化产生的中间类（如 BaseCrud[User]）"""
        for base in bases:
            origin = getattr(base, "__origin__", None)
            if origin is not None:
                return True
        return False


class BaseCRUD(abc.ABC, Generic[T], metaclass=BaseCRUDMeta):
    model_cls: Type[SQLModel]

    @classmethod
    def get_pk_name(cls) -> str:
        """获取模型的主键字段名，默认为 'id'"""
        if hasattr(cls.model_cls, "__table__"):
            primary_keys = cls.model_cls.__table__.primary_key.columns.keys()
            if primary_keys:
                return primary_keys[0]
        return "id"

    @classmethod
    def add(cls, db: Session, item: T, commit: bool = True) -> T | None:  # 改: SQLModel -> M
        """
        创建单条记录并保存到数据库。
        :param db: 数据库 Session
        :param item: 要创建的模型对象实例
        :param commit: 是否提交事务，默认为 True
        :return: 创建成功后的模型实例
        """
        db.add(item)
        if commit:
            db.commit()
            db.refresh(item)
        return item

    @classmethod
    def add_all(cls, db: Session, items: list[T], commit: bool = True) -> list[T] | None:  # 改
        """
        批量创建多条记录并保存到数据库。
        :param db: 数据库 Session
        :param items: 要创建的模型对象列表
        :param commit: 是否提交事务，默认为 True
        :return: None
        """
        db.add_all(items)
        if commit:
            db.commit()

    @classmethod
    def update_by_id(cls, db: Session, _id: int, item: T, commit: bool = True):  # 改
        """
        根据主键 ID 更新单个对象的字段。
        :param db: 数据库 Session
        :param _id: 主键 ID 的值
        :param item: 包含要更新字段及值的模型对象
        :param commit: 是否提交事务，默认为 True
        """
        if _id is None:
            return

        pk_name = cls.get_pk_name()
        stmt = (
            update(cls.model_cls)
            .where(SqlBuilder.get_conditions_from_dict(cls.model_cls, {pk_name: _id}))
            .values(SqlBuilder.get_values(item))
        )

        db.exec(stmt)
        if commit:
            db.commit()

    @classmethod
    def batch_update_by_ids(cls, db: Session, _ids: list[int], item: T, commit: bool = True):  # 改
        """
        根据主键 ID 列表，将多条记录更新为相同的值。
        :param db: 数据库 Session
        :param _ids: 主键 ID 列表
        :param item: 包含要更新字段及值的模型对象
        :param commit: 是否提交事务，默认为 True
        """
        if not _ids:
            return

        pk_name = cls.get_pk_name()
        pk_col = getattr(cls.model_cls, pk_name)

        stmt = (
            update(cls.model_cls)
            .where(pk_col.in_(_ids))
            .values(SqlBuilder.get_values(item))
        )

        db.exec(stmt)
        if commit:
            db.commit()

    @classmethod
    def batch_update(cls, db: Session, items: list[T], commit: bool = True, skip_no_pk: bool = True):
        """
        批量更新对象列表，根据每个对象的主键进行单独更新。
        :param db: 数据库 Session
        :param items: 要更新的对象列表
        :param skip_no_pk: 如果对象没有主键，是否跳过。True 则跳过，False 则抛出 ValueError 异常
        :param commit: 是否在最后提交事务
        """
        if not items:
            return

        pk_name = cls.get_pk_name()

        for item in items:
            pk_value = getattr(item, pk_name, None)
            if pk_value is None:
                if skip_no_pk:
                    continue
                else:
                    raise ValueError(f"更新失败：对象缺失主键 '{pk_name}'")

            stmt = (
                update(cls.model_cls)
                .where(SqlBuilder.get_conditions_from_dict(cls.model_cls, {pk_name: pk_value}))
                .values(SqlBuilder.get_values(item))
            )
            db.exec(stmt)

        if commit:
            db.commit()

    @classmethod
    def one(
        cls,
        db: Session,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None,
        order_by: list[OrderCondition] | None = None,
        for_update: bool = False
    ) -> T | None:
        """
        根据条件查询单条记录。
        :param db: 数据库 Session
        :param cond: 查询条件，支持模型实例、字典、条件列表或基础条件对象
        :param order_by: 排序条件列表
        :param for_update: 是否使用 for update 加行锁
        :return: 查询到的第一条模型记录，未找到返回 None
        """
        stmt = select(cls.model_cls)

        if cond is not None:
            if isinstance(cond, SQLModel):
                where_cond = SqlBuilder.get_conditions(cond)
            elif isinstance(cond, list):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, cond)
            elif isinstance(cond, BaseCondition):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, [cond])
            else:
                where_cond = SqlBuilder.get_conditions_from_dict(cls.model_cls, cond)

            if where_cond is not True:
                stmt = stmt.where(where_cond)
        else:
            if 'is_del' in cls.model_cls.model_fields:
                stmt = stmt.where(getattr(cls.model_cls, 'is_del') == False)

        stmt = SqlBuilder.apply_order_by(stmt, cls.model_cls, order_by)

        if for_update:
            stmt = stmt.with_for_update()

        return cast(T, db.exec(stmt).first())

    @classmethod
    def all(
        cls,
        db: Session,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None,
        order_by: list[OrderCondition] | None = None,
        for_update: bool = False
    ) -> list[T]:
        """
        根据条件查询所有符合的记录。
        :param db: 数据库 Session
        :param cond: 查询条件，支持模型实例、字典、条件列表或基础条件对象
        :param order_by: 排序条件列表
        :param for_update: 是否使用 for update 加行锁
        :return: 符合条件的模型记录列表
        """
        stmt = select(cls.model_cls)

        if cond is not None:
            if isinstance(cond, SQLModel):
                where_cond = SqlBuilder.get_conditions(cond)
            elif isinstance(cond, list):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, cond)
            elif isinstance(cond, BaseCondition):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, [cond])
            else:
                where_cond = SqlBuilder.get_conditions_from_dict(cls.model_cls, cond)

            if where_cond is not True:
                stmt = stmt.where(where_cond)
        else:
            if 'is_del' in cls.model_cls.model_fields:
                stmt = stmt.where(getattr(cls.model_cls, 'is_del') == False)

        stmt = SqlBuilder.apply_order_by(stmt, cls.model_cls, order_by)

        if for_update:
            stmt = stmt.with_for_update()

        return cast(list[T], db.exec(stmt).all())

    @classmethod
    def _build_where(cls, cond: T | dict[str | Any, BaseCondition | Any] | list[
        BaseCondition] | BaseCondition | None = None) -> Any:
        """
        内部方法，用于构建并统一处理 WHERE 查询条件。
        :param cond: 查询条件对象
        :return: SQLAlchemy 兼容的过滤条件（表达式）
        """
        if cond is None:
            if 'is_del' in cls.model_cls.model_fields:
                return getattr(cls.model_cls, 'is_del') == False
            return True
        if isinstance(cond, SQLModel):
            return SqlBuilder.get_conditions(cond)
        if isinstance(cond, list):
            return SqlBuilder.get_conditions_from_list(cls.model_cls, cond)
        if isinstance(cond, BaseCondition):
            return SqlBuilder.get_conditions_from_list(cls.model_cls, [cond])
        return SqlBuilder.get_conditions_from_dict(cls.model_cls, cond)

    @classmethod
    def count(
        cls,
        db: Session,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None
    ) -> int:
        """
        统计符合条件的记录总数。
        :param db: 数据库 Session
        :param cond: 查询条件对象
        :return: 符合条件的记录数
        """
        where_cond = cls._build_where(cond)
        stmt = select(func.count()).select_from(cls.model_cls)
        if where_cond is not True:
            stmt = stmt.where(where_cond)
        return cast(int, db.exec(stmt).first() or 0)

    @classmethod
    def page(
        cls,
        db: Session,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None,
        order_by: list[OrderCondition] | None = None,
        page: int = 1,
        size: int = 10
    ) -> Page:
        """
        分页查询符合条件的记录。
        :param db: 数据库 Session
        :param cond: 查询条件对象
        :param order_by: 排序条件列表
        :param page: 当前页码，从 1 开始
        :param size: 每页数量
        :return: 包含分页数据与信息的 Page 实例
        """
        total = cls.count(db, cond)
        pages = (total + size - 1) // size if total else 0

        data = []
        if total > 0:
            where_cond = cls._build_where(cond)
            stmt = select(cls.model_cls)
            if where_cond is not True:
                stmt = stmt.where(where_cond)

            stmt = SqlBuilder.apply_order_by(stmt, cls.model_cls, order_by)
            stmt = stmt.offset((page - 1) * size).limit(size)
            data = list(db.exec(stmt).all())

        return Page(data=data, total=total, pages=pages, current=page)

    @classmethod
    async def add_async(cls, db: AsyncSession, item: T, commit: bool = True) -> T | None:
        db.add(item)
        if commit:
            await db.commit()
            await db.refresh(item)
        return item

    @classmethod
    async def add_all_async(cls, db: AsyncSession, items: list[T], commit: bool = True) -> list[T] | None:
        db.add_all(items)
        if commit:
            await db.commit()

    @classmethod
    async def update_by_id_async(cls, db: AsyncSession, _id: int, item: T, commit: bool = True):
        if _id is None:
            return

        pk_name = cls.get_pk_name()
        stmt = (
            update(cls.model_cls)
            .where(SqlBuilder.get_conditions_from_dict(cls.model_cls, {pk_name: _id}))
            .values(SqlBuilder.get_values(item))
        )

        await db.exec(stmt)
        if commit:
            await db.commit()

    @classmethod
    async def batch_update_by_ids_async(cls, db: AsyncSession, _ids: list[int], item: T, commit: bool = True):
        if not _ids:
            return

        pk_name = cls.get_pk_name()
        pk_col = getattr(cls.model_cls, pk_name)

        stmt = (
            update(cls.model_cls)
            .where(pk_col.in_(_ids))
            .values(SqlBuilder.get_values(item))
        )

        await db.exec(stmt)
        if commit:
            await db.commit()

    @classmethod
    async def batch_update_async(cls, db: AsyncSession, items: list[T], commit: bool = True, skip_no_pk: bool = True):
        if not items:
            return

        pk_name = cls.get_pk_name()

        for item in items:
            pk_value = getattr(item, pk_name, None)
            if pk_value is None:
                if skip_no_pk:
                    continue
                else:
                    raise ValueError(f"更新失败：对象缺失主键 '{pk_name}'")

            stmt = (
                update(cls.model_cls)
                .where(SqlBuilder.get_conditions_from_dict(cls.model_cls, {pk_name: pk_value}))
                .values(SqlBuilder.get_values(item))
            )
            await db.exec(stmt)

        if commit:
            await db.commit()

    @classmethod
    async def one_async(
        cls,
        db: AsyncSession,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None,
        order_by: list[OrderCondition] | None = None,
        for_update: bool = False
    ) -> T | None:
        stmt = select(cls.model_cls)

        if cond is not None:
            if isinstance(cond, SQLModel):
                where_cond = SqlBuilder.get_conditions(cond)
            elif isinstance(cond, list):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, cond)
            elif isinstance(cond, BaseCondition):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, [cond])
            else:
                where_cond = SqlBuilder.get_conditions_from_dict(cls.model_cls, cond)

            if where_cond is not True:
                stmt = stmt.where(where_cond)
        else:
            if 'is_del' in cls.model_cls.model_fields:
                stmt = stmt.where(getattr(cls.model_cls, 'is_del') == False)

        stmt = SqlBuilder.apply_order_by(stmt, cls.model_cls, order_by)

        if for_update:
            stmt = stmt.with_for_update()

        result = await db.exec(stmt)
        return cast(T, result.first())

    @classmethod
    async def all_async(
        cls,
        db: AsyncSession,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None,
        order_by: list[OrderCondition] | None = None,
        for_update: bool = False
    ) -> list[T]:
        stmt = select(cls.model_cls)

        if cond is not None:
            if isinstance(cond, SQLModel):
                where_cond = SqlBuilder.get_conditions(cond)
            elif isinstance(cond, list):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, cond)
            elif isinstance(cond, BaseCondition):
                where_cond = SqlBuilder.get_conditions_from_list(cls.model_cls, [cond])
            else:
                where_cond = SqlBuilder.get_conditions_from_dict(cls.model_cls, cond)

            if where_cond is not True:
                stmt = stmt.where(where_cond)
        else:
            if 'is_del' in cls.model_cls.model_fields:
                stmt = stmt.where(getattr(cls.model_cls, 'is_del') == False)

        stmt = SqlBuilder.apply_order_by(stmt, cls.model_cls, order_by)

        if for_update:
            stmt = stmt.with_for_update()

        result = await db.exec(stmt)
        return cast(list[T], list(result.all()))

    @classmethod
    async def count_async(
        cls,
        db: AsyncSession,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None
    ) -> int:
        where_cond = cls._build_where(cond)
        stmt = select(func.count()).select_from(cls.model_cls)
        if where_cond is not True:
            stmt = stmt.where(where_cond)
        result = await db.exec(stmt)
        return cast(int, result.first() or 0)

    @classmethod
    async def page_async(
        cls,
        db: AsyncSession,
        cond: T | dict[str | Any, BaseCondition | Any] | list[BaseCondition] | BaseCondition | None = None,
        order_by: list[OrderCondition] | None = None,
        page: int = 1,
        size: int = 10
    ) -> Page:
        total = await cls.count_async(db, cond)
        pages = (total + size - 1) // size if total else 0

        data = []
        if total > 0:
            where_cond = cls._build_where(cond)
            stmt = select(cls.model_cls)
            if where_cond is not True:
                stmt = stmt.where(where_cond)

            stmt = SqlBuilder.apply_order_by(stmt, cls.model_cls, order_by)
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await db.exec(stmt)
            data = list(result.all())

        return Page(data=data, total=total, pages=pages, current=page)


class SqlBuilder:

    @classmethod
    def apply_order_by(
        cls,
        stmt,
        model_cls: Type[SQLModel],
        order_by: list[OrderCondition] | None = None,
    ):
        """
        为 SQLModel 查询语句应用排序条件。
        :param stmt: 查询语句 (select object)
        :param model_cls: 关联的 SQLModel 类
        :param order_by: 排序条件列表
        :return: 应用排序后的查询语句
        """
        if not order_by:
            return stmt

        model_field_names = set(model_cls.model_fields.keys())
        seen: set[str] = set()
        order_clauses = []

        for cond in order_by:
            field_name, column = cls._resolve_order_field(model_cls, cond.field)

            if column is None:
                continue

            if field_name and field_name not in model_field_names:
                continue

            if field_name in seen:
                continue
            seen.add(cast(str, field_name))

            if cond.direction == OrderDirection.DESC:
                order_clauses.append(desc(column))
            else:
                order_clauses.append(asc(column))

        if order_clauses:
            stmt = stmt.order_by(*order_clauses)

        return stmt

    @classmethod
    def _resolve_order_field(
        cls,
        model_cls: Type[SQLModel],
        field: Any,
    ) -> tuple[str | None, Any]:
        """
        解析排序字段的名称及对应列对象。
        :param model_cls: 关联的 SQLModel 类
        :param field: 字段名称或列对象
        :return: (字段名, 对应的列对象) 元组
        """
        if isinstance(field, str):
            col = getattr(model_cls, field, None)
            return field, col

        field_name = cls._get_field_name(field)
        return field_name, field

    @classmethod
    def get_conditions(cls, orm: SQLModel | None) -> Any:
        """
        从 SQLModel 对象提取非空属性，构建等值查询条件。
        :param orm: SQLModel 实例
        :return: SQLAlchemy 的条件子句
        """
        if not orm:
            return True

        model_fields = orm.model_dump().keys()
        query_dict = {
            k: v for k, v in orm.model_dump(exclude_unset=True, exclude_none=True).items()
            if v is not None
        }

        if 'is_del' in model_fields and 'is_del' not in query_dict:
            query_dict['is_del'] = FieldCondition(value=False)

        query_dict = {
            k: (FieldCondition(value=v) if not isinstance(v, BaseCondition) else v)
            for k, v in query_dict.items()
        }

        return cls._build_conditions(orm.__class__, query_dict)

    @classmethod
    def get_conditions_from_dict(cls, model_cls: Type[SQLModel], cond_dict: dict[str | Any, Any]) -> Any:
        """
        从字典中构建查询条件。
        :param model_cls: 关联的 SQLModel 类
        :param cond_dict: 包含字段与对应值的字典
        :return: SQLAlchemy 的条件子句
        """
        if 'is_del' in model_cls.model_fields and not any(
            cls._get_field_name(k) == 'is_del' for k in cond_dict.keys()
        ):
            cond_dict['is_del'] = FieldCondition(value=False)

        processed_cond = {
            k: (FieldCondition(value=v) if not isinstance(v, BaseCondition) else v)
            for k, v in cond_dict.items()
        }

        return cls._build_conditions(model_cls, processed_cond)

    @classmethod
    def _has_field(cls, conds: list[BaseCondition], field_name: str) -> bool:
        """
        检查条件列表中是否包含对指定字段名的限制。
        :param conds: 基础条件列表
        :param field_name: 要检查的字段名
        :return: 如果包含则返回 True，否则返回 False
        """
        for cond in conds:
            if isinstance(cond, FieldCondition):
                name = cond.field if isinstance(cond.field, str) else getattr(cond.field, 'name', None)
                if name == field_name:
                    return True
            elif isinstance(cond, LogicalCondition):
                if cls._has_field(cond.conditions, field_name):
                    return True
        return False

    @classmethod
    def build_condition_clause(cls, model_cls: Type[SQLModel], cond: BaseCondition, default_field: Any = None) -> Any:
        """
        根据条件对象构建单一的 SQLAlchemy 条件子句。
        :param model_cls: 关联的 SQLModel 类
        :param cond: BaseCondition 基础条件对象
        :param default_field: 默认要绑定的字段对象
        :return: 单一的条件子句
        """
        from sqlmodel import and_, or_
        if isinstance(cond, FieldCondition):
            field = cond.field if cond.field is not None else default_field
            if isinstance(field, str):
                field = getattr(model_cls, field, None)
            if field is None:
                return None
            return cls._apply_operator(field, cond.op, cond.value)
        elif isinstance(cond, LogicalCondition):
            clauses = []
            for sub_cond in cond.conditions:
                clause = cls.build_condition_clause(model_cls, sub_cond, default_field)
                if clause is not None:
                    clauses.append(clause)
            if not clauses:
                return None
            if len(clauses) == 1:
                return clauses[0]
            if cond.logical_op == "and":
                return and_(*clauses)
            else:
                return or_(*clauses)
        return None

    @classmethod
    def get_conditions_from_list(cls, model_cls: Type[SQLModel], cond_list: list[BaseCondition]) -> Any:
        """
        从基础条件列表构建复合 SQLAlchemy 条件子句（默认使用 AND 组合）。
        :param model_cls: 关联的 SQLModel 类
        :param cond_list: 基础条件对象列表
        :return: 组合后的 SQLAlchemy 条件子句
        """
        from sqlmodel import and_
        has_is_del_condition = cls._has_field(cond_list, 'is_del')
        if 'is_del' in model_cls.model_fields and not has_is_del_condition:
            is_del_field = getattr(model_cls, 'is_del')
            cond_list = cond_list + [FieldCondition(value=False, field=is_del_field)]

        conditions = []
        for cond in cond_list:
            clause = cls.build_condition_clause(model_cls, cond)
            if clause is not None:
                conditions.append(clause)

        if not conditions:
            return True
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return and_(*conditions)

    @classmethod
    def _build_conditions(cls, model_cls: Type[SQLModel], cond_dict: dict[str | Any, BaseCondition]) -> Any:
        """
        内部方法，根据字典构建最终的 SQLAlchemy AND 逻辑条件子句。
        :param model_cls: 关联的 SQLModel 类
        :param cond_dict: 字段到基础条件对象的映射字典
        :return: 组合后的 SQLAlchemy 条件子句
        """
        from sqlmodel import and_
        if not cond_dict:
            return True

        conditions = []
        for key, condition in cond_dict.items():
            field_name = cls._get_field_name(key)

            field = getattr(model_cls, field_name, None)
            if not field:
                continue

            clause = cls.build_condition_clause(model_cls, condition, default_field=field)
            if clause is not None:
                conditions.append(clause)

        if not conditions:
            return True
        if len(conditions) == 1:
            return conditions[0]
        return and_(*conditions)

    @staticmethod
    def _apply_operator(field, op: ConditionOperator, value: Any):
        """
        根据操作符枚举，对指定列应用相应的 SQLAlchemy 过滤操作。
        :param field: 列对象
        :param op: ConditionOperator 操作符枚举
        :param value: 匹配值
        :return: SQLAlchemy 的列级过滤条件
        """
        if op == ConditionOperator.EQ:
            return field == value
        elif op == ConditionOperator.NE:
            return field != value
        elif op == ConditionOperator.GT:
            return field > value
        elif op == ConditionOperator.LT:
            return field < value
        elif op == ConditionOperator.GE:
            return field >= value
        elif op == ConditionOperator.LE:
            return field <= value
        elif op == ConditionOperator.IN:
            return field.in_(value)
        elif op == ConditionOperator.NOT_IN:
            return field.not_in(value)
        elif op == ConditionOperator.LIKE:
            return field.like(f"%{value}%")
        elif op == ConditionOperator.CONTAINS:
            return field.contains(value)
        return None

    @staticmethod
    def _get_field_name(key: str | Any) -> str:
        """
        获取字段或键对应的字符串名称。
        :param key: 字符串或包含 key/name 属性的字段对象
        :return: 字段的字符串名称
        """
        if isinstance(key, str):
            return key
        if hasattr(key, "key"):
            return key.key
        if hasattr(key, "name"):
            return key.name
        return str(key)

    @staticmethod
    def get_values(values: SQLModel) -> dict[str, Any]:
        """
        提取 SQLModel 对象中有效的值字典（排除未设置和 None 值），用于更新操作。
        :param values: 包含更新数据的 SQLModel 实例
        :return: 有效字段及值的字典
        """
        return values.model_dump(exclude_unset=True, exclude_none=True)


class Page(BaseModel):
    total: int
    pages: int
    current: int
    data: list[Any]
