"""认证接口。"""
from ..common import read_json_body, require_method
from ..decorators import api_view
from ..services import auth_service


@api_view
def register(request):
    require_method(request, "POST")
    return auth_service.register(read_json_body(request))


@api_view
def login(request):
    require_method(request, "POST")
    return auth_service.login(read_json_body(request), request)


@api_view
def me(request):
    require_method(request, "GET")
    return auth_service.current_user(request)


@api_view
def logout(request):
    require_method(request, "POST")
    auth_service.logout(request)
    return None
