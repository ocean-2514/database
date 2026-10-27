"""视图装饰器：统一响应、异常转换、登录与管理员校验。"""
import json
import logging
from functools import wraps

from django.views.decorators.csrf import csrf_exempt

from .common import error, json_response, ok
from .exceptions import AdminRequired, ApiError, Unauthorized

logger = logging.getLogger("api")


def session_user(request) -> dict | None:
    user_id = request.session.get("userId")
    if user_id is None:
        return None
    return {
        "userId": user_id,
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    }


def require_login(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = session_user(request)
        if user is None:
            raise Unauthorized("请先登录")
        request.api_user = user
        return view(request, *args, **kwargs)

    return wrapper


def require_admin(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = session_user(request)
        if user is None:
            raise Unauthorized("请先登录")
        if user.get("role") != "admin":
            raise AdminRequired("需要管理员权限")
        request.api_user = user
        return view(request, *args, **kwargs)

    return wrapper


def api_view(view):
    """把一个返回 Python 数据结构的函数包装成统一 JSON 接口。"""

    @csrf_exempt
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            result = view(request, *args, **kwargs)
            return json_response(ok(result))
        except ApiError as exc:
            return json_response(error(exc.code, exc.message), status=exc.http_status)
        except json.JSONDecodeError:
            return json_response(error(400, "请求体格式不正确"))
        except Exception as exc:  # 与原实现 GlobalExceptionHandler 的兜底一致
            logger.exception("服务器内部错误")
            return json_response(error(500, f"服务器内部错误: {exc}"))

    return wrapper
