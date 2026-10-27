"""收藏接口（全部需要登录）。"""
from ..common import parse_path_int, require_method
from ..decorators import api_view, require_login
from ..services import favorite_service


@api_view
@require_login
def favorite(request, poem_id):
    poem_id = parse_path_int(poem_id, "poemId")
    user_id = request.api_user["userId"]

    if request.method == "POST":
        favorite_service.add(
            user_id,
            poem_id,
            {"favoriteType": request.GET.get("favoriteType")},
        )
        return None
    if request.method == "DELETE":
        favorite_service.cancel(user_id, poem_id)
        return None
    require_method(request, "POST", "DELETE")
    return None


@api_view
@require_login
def my_favorites(request):
    require_method(request, "GET")
    return favorite_service.list_favorites(request.api_user["userId"], request.GET)
