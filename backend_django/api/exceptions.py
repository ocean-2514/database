"""业务异常。

原实现的行为：
- 参数/业务异常由 GlobalExceptionHandler 转成 HTTP 200 + {code:400/404...}；
- 登录/管理员拦截器直接返回 HTTP 401/403。
这里用 http_status 区分两种行为。
"""


class ApiError(Exception):
    code = 500
    http_status = 200

    def __init__(self, message: str, code: int | None = None, http_status: int | None = None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if http_status is not None:
            self.http_status = http_status


class BadRequest(ApiError):
    code = 400


class NotFound(ApiError):
    code = 404


class BusinessForbidden(ApiError):
    """资源级权限失败：HTTP 200 + code 403，与原 Service 抛 BusinessException 一致。"""

    code = 403


class Unauthorized(ApiError):
    """端点级登录校验失败：HTTP 401。"""

    code = 401
    http_status = 401


class AdminRequired(ApiError):
    """端点级管理员校验失败：HTTP 403。"""

    code = 403
    http_status = 403


class MethodNotAllowed(ApiError):
    code = 405
    http_status = 405
