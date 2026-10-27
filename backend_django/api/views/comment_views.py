"""评论接口：列表公开，发表/修改/删除需登录。"""
from ..common import parse_path_int, read_json_body, require_method
from ..decorators import api_view, require_login, session_user
from ..exceptions import Unauthorized
from ..services import comment_service


@api_view
def comments(request, poem_id):
    poem_id = parse_path_int(poem_id, "poemId")
    if request.method == "GET":
        return comment_service.list_comments(poem_id, request.GET)
    if request.method == "POST":
        # 列表公开，只有发表评论需要登录；因此不能给整个视图加 @require_login。
        user = session_user(request)
        if user is None:
            raise Unauthorized("请先登录")
        return {
            "commentId": comment_service.add(
                user["userId"], poem_id, read_json_body(request)
            )
        }
    require_method(request, "GET", "POST")
    return None


@api_view
@require_login
def comment_detail(request, comment_id):
    comment_id = parse_path_int(comment_id, "commentId")
    user = request.api_user
    if request.method == "PUT":
        comment_service.edit(user["userId"], comment_id, read_json_body(request))
        return None
    if request.method == "DELETE":
        comment_service.delete(user["userId"], user.get("role"), comment_id)
        return None
    require_method(request, "PUT", "DELETE")
    return None
