"""收藏业务。"""
from ..common import normalize_page, page_result, parse_int, text_value
from ..db import is_duplicate_error
from ..exceptions import BadRequest
from ..repositories import favorite_repo, poem_repo


def add(user_id: int, poem_id: int, data: dict) -> None:
    if poem_repo.count_published_poem(poem_id) == 0:
        raise BadRequest(f"诗歌不存在或已下架: id={poem_id}")
    if favorite_repo.find_user_favorite(user_id, poem_id) is not None:
        raise BadRequest("已收藏过该诗歌")

    favorite_type = text_value(data, "favoriteType")
    if favorite_type is None or not favorite_type.strip():
        favorite_type = "默认"
    else:
        favorite_type = favorite_type.strip()

    try:
        favorite_repo.insert_favorite(user_id, poem_id, favorite_type)
    except Exception as exc:
        # 并发下 UNIQUE(user_id, poem_id) 仍可能触发，转换为友好提示
        if is_duplicate_error(exc):
            raise BadRequest("已收藏过该诗歌") from exc
        raise


def cancel(user_id: int, poem_id: int) -> None:
    if favorite_repo.find_user_favorite(user_id, poem_id) is None:
        raise BadRequest("尚未收藏该诗歌")
    favorite_repo.delete_favorite(user_id, poem_id)


def list_favorites(user_id: int, params) -> dict:
    page, page_size = normalize_page(
        parse_int(params.get("page"), "page", 1),
        parse_int(params.get("pageSize"), "pageSize", 10),
    )
    total = favorite_repo.count_user_favorites(user_id)
    rows = (
        []
        if total == 0
        else favorite_repo.list_user_favorites(user_id, (page - 1) * page_size, page_size)
    )
    return page_result(total, page, page_size, rows)
