"""HTTP 响应、分页、JSON 与参数类型转换。

这里刻意保持 原实现的字段名（camelCase），使前端无需改动。
"""
import json
from decimal import Decimal
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from .exceptions import BadRequest, MethodNotAllowed


class ApiJSONEncoder(DjangoJSONEncoder):
    """DjangoJSONEncoder 会把 Decimal 输出成字符串，这里改成数字。"""

    def default(self, obj: Any):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def ok(data: Any = None) -> dict:
    return {"code": 200, "message": "success", "data": data}


def error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}


def json_response(payload: dict, status: int = 200) -> JsonResponse:
    return JsonResponse(
        payload,
        status=status,
        encoder=ApiJSONEncoder,
        json_dumps_params={"ensure_ascii": False},
    )


def page_result(total: int, page: int, page_size: int, rows: list) -> dict:
    return {
        "total": int(total),
        "page": page,
        "pageSize": page_size,
        "list": rows,
    }


def require_method(request, *methods: str) -> None:
    if request.method not in methods:
        raise MethodNotAllowed(f"请求方法不允许: {request.method}")


def read_json_body(request) -> dict:
    """读取 JSON 对象请求体；空请求体按空对象处理。"""
    raw = request.body
    if not raw:
        return {}
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BadRequest("请求体格式不正确") from exc
    if not isinstance(data, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    return data


def parse_int(value: Any, name: str, default: int | None = None) -> int | None:
    """把 JSON/查询参数转换成整数，失败时给出与原实现一致的提示。"""
    if value is None:
        return default
    if isinstance(value, bool):
        raise BadRequest(f"参数类型不正确: {name}")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise BadRequest(f"参数类型不正确: {name}")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        try:
            return int(text, 10)
        except ValueError as exc:
            raise BadRequest(f"参数类型不正确: {name}") from exc
    raise BadRequest(f"参数类型不正确: {name}")


def parse_path_int(raw: str, name: str = "id") -> int:
    value = parse_int(raw, name)
    if value is None:
        raise BadRequest(f"参数类型不正确: {name}")
    return value


def normalize_page(page: int | None, page_size: int | None) -> tuple[int, int]:
    """与原 Service 层一致：页码最小 1，页大小默认 10、上限 50。"""
    p = 1 if page is None or page < 1 else page
    size = 10 if page_size is None or page_size < 1 else min(page_size, 50)
    return p, size


def text_value(data: dict, key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    raise BadRequest(f"参数类型不正确: {key}")


def int_value(data: dict, key: str) -> int | None:
    return parse_int(data.get(key), key, None)
