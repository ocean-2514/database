"""评分接口（全部需要登录）。"""
from ..common import parse_path_int, require_method
from ..decorators import api_view, require_login
from ..services import rating_service


@api_view
@require_login
def rating(request, poem_id):
    poem_id = parse_path_int(poem_id, "poemId")
    user_id = request.api_user["userId"]

    if request.method == "PUT":
        return rating_service.rate(user_id, poem_id, request.GET.get("score"))
    if request.method == "GET":
        return rating_service.my_rating(user_id, poem_id)
    if request.method == "DELETE":
        rating_service.cancel(user_id, poem_id)
        return None
    require_method(request, "PUT", "GET", "DELETE")
    return None
