"""评分业务。"""
from ..common import parse_int
from ..exceptions import BadRequest
from ..repositories import poem_repo, rating_repo


def rate(user_id: int, poem_id: int, score_raw) -> str:
    score = parse_int(score_raw, "score", None)
    if score is None or score < 1 or score > 5:
        raise BadRequest("评分需为 1-5 的整数")
    if poem_repo.count_published_poem(poem_id) == 0:
        raise BadRequest(f"诗歌不存在或已下架: id={poem_id}")

    rows = rating_repo.upsert(user_id, poem_id, score)
    return "created" if rows == 1 else "updated"


def my_rating(user_id: int, poem_id: int) -> dict | None:
    return rating_repo.find_by_user_and_poem(user_id, poem_id)


def cancel(user_id: int, poem_id: int) -> None:
    if rating_repo.find_by_user_and_poem(user_id, poem_id) is None:
        raise BadRequest("尚未评分")
    rating_repo.delete_rating(user_id, poem_id)
