"""评论业务：读公开，写需登录，改删校验属主。"""
from ..common import normalize_page, page_result, parse_int, text_value
from ..exceptions import BadRequest, BusinessForbidden, NotFound
from ..repositories import comment_repo, poem_repo

MAX_CONTENT_LENGTH = 1000


def add(user_id: int, poem_id: int, data: dict) -> int:
    content = _validate_content(data)
    if poem_repo.count_published_poem(poem_id) == 0:
        raise BadRequest(f"诗歌不存在或已下架: id={poem_id}")
    return comment_repo.insert_comment(user_id, poem_id, content)


def edit(user_id: int, comment_id: int, data: dict) -> None:
    content = _validate_content(data)
    # role=None 表示不允许管理员代改他人评论
    comment = _require_comment(comment_id, user_id, None)
    comment_repo.update_content(comment["commentId"], content)


def delete(user_id: int, role: str | None, comment_id: int) -> None:
    comment = _require_comment(comment_id, user_id, role)
    comment_repo.delete_comment(comment["commentId"])


def list_comments(poem_id: int, params) -> dict:
    if poem_repo.count_published_poem(poem_id) == 0:
        raise BadRequest(f"诗歌不存在或已下架: id={poem_id}")

    page, page_size = normalize_page(
        parse_int(params.get("page"), "page", 1),
        parse_int(params.get("pageSize"), "pageSize", 10),
    )
    total = comment_repo.count_by_poem(poem_id)
    rows = (
        []
        if total == 0
        else comment_repo.list_by_poem(poem_id, (page - 1) * page_size, page_size)
    )
    return page_result(total, page, page_size, rows)


def _require_comment(comment_id: int, user_id: int, role: str | None) -> dict:
    comment = comment_repo.find_by_comment_id(comment_id)
    if comment is None:
        raise NotFound(f"评论不存在: id={comment_id}")

    is_owner = comment["userId"] == user_id
    is_admin = role == "admin"
    if not is_owner and not is_admin:
        raise BusinessForbidden("只能操作自己的评论")
    return comment


def _validate_content(data: dict) -> str:
    content = (text_value(data, "content") or "").strip()
    if not content:
        raise BadRequest("评论内容不能为空")
    if len(content) > MAX_CONTENT_LENGTH:
        raise BadRequest(f"评论内容不能超过 {MAX_CONTENT_LENGTH} 字")
    return content
