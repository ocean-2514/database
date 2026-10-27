"""手写 SQL 的统一执行入口。

与原项目一致，数据访问层不依赖 ORM。查询结果直接使用 SQL 别名，
别名就是返回给前端的 camelCase 字段名。
"""
from decimal import Decimal
from typing import Any

from django.db import connection


def _normalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def _rows(cursor) -> list[dict]:
    if cursor.description is None:
        return []
    columns = [column[0] for column in cursor.description]
    return [
        {column: _normalize(value) for column, value in zip(columns, row)}
        for row in cursor.fetchall()
    ]


def fetch_all(sql: str, params: list | tuple | None = None) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        return _rows(cursor)


def fetch_one(sql: str, params: list | tuple | None = None) -> dict | None:
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def fetch_scalar(sql: str, params: list | tuple | None = None):
    row = fetch_one(sql, params)
    if not row:
        return None
    return next(iter(row.values()))


def execute(sql: str, params: list | tuple | None = None) -> tuple[int, int]:
    """执行写操作，返回 (受影响行数, 自增主键)。"""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        return cursor.rowcount, cursor.lastrowid


def call_procedure(sql: str, params: list | tuple | None = None) -> list[dict]:
    """调用返回结果集的存储过程，并消费掉可能存在的后续结果集。"""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        rows = _rows(cursor)
        while cursor.nextset():
            pass
        return rows


def call_procedure_with_out(
    sql: str,
    params: list | tuple,
    out_variable: str = "@poetry_out_id",
) -> int | None:
    """调用带 OUT 参数的存储过程。

    MySQL 的 OUT 参数通过会话变量承接，因此先初始化变量，执行 CALL，
    再用 SELECT 读取。整个过程必须在同一个连接内完成。
    """
    with connection.cursor() as cursor:
        cursor.execute(f"SET {out_variable} = 0")
        cursor.execute(sql, params)
        while cursor.nextset():
            pass
        cursor.execute(f"SELECT {out_variable} AS value")
        row = cursor.fetchone()
        return None if row is None else int(row[0])


def mysql_error_message(exc: Exception) -> str:
    """提取 MySQL SIGNAL / 约束错误中的可用中文提示。"""
    args = getattr(exc, "args", ())
    if len(args) >= 2 and isinstance(args[0], int):
        return str(args[1])
    return str(exc)


def is_duplicate_error(exc: Exception) -> bool:
    """MySQL 1062：违反唯一约束。"""
    args = getattr(exc, "args", ())
    return bool(args) and args[0] == 1062

