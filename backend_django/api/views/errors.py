"""项目级 404/500 处理器与 /api/ 兜底。"""
from ..common import error, json_response


def not_found(request, exception):
    return json_response(error(404, "资源不存在"), status=404)


def server_error(request):
    return json_response(error(500, "服务器内部错误"), status=500)


def api_not_found(request, *args, **kwargs):
    """未匹配到任何 API 路由时也返回统一 JSON，而不是 Django 的 HTML 404。"""
    return json_response(error(404, "资源不存在"), status=404)
