"""管理端业务：诗人、诗歌、诗集、流派。

数据库端防线在本层转换为友好提示：
- 删除有作品的诗人 -> 触发器 SIGNAL -> 400；
- 物理删除有互动记录的诗歌 -> RESTRICT 外键 -> 400；
- 新建诗集走事务存储过程，部分诗歌 ID 无效时整体回滚；
- 流派重名 -> UNIQUE 约束 -> 400。
"""
from ..common import int_value, text_value
from ..db import is_duplicate_error, mysql_error_message
from ..exceptions import BadRequest, NotFound
from ..repositories import (
    collection_repo,
    genre_repo,
    poem_repo,
    poet_repo,
)


def _java_id(value) -> str:
    return "null" if value is None else str(value)


# ---------------- 诗人 ----------------


def list_poets() -> list[dict]:
    return poet_repo.list_all()


def _poet_payload(data: dict, for_create: bool) -> dict:
    name = text_value(data, "name")
    gender = text_value(data, "gender")

    if for_create:
        if name is None or not name.strip():
            raise BadRequest("诗人姓名不能为空")
        if gender is None or not gender.strip():
            gender = "男"

    return {
        "name": name,
        "penName": text_value(data, "penName"),
        "gender": gender,
        "birthYear": int_value(data, "birthYear"),
        "deathYear": int_value(data, "deathYear"),
        "nationality": text_value(data, "nationality"),
        "biography": text_value(data, "biography"),
    }


def add_poet(data: dict) -> dict:
    poet = _poet_payload(data, for_create=True)
    poet_id = poet_repo.insert(poet)
    return {"poetId": poet_id}


def update_poet(poet_id: int, data: dict) -> None:
    _require_poet(poet_id)
    poet = _poet_payload(data, for_create=False)
    poet_repo.update(poet_id, poet)


def delete_poet(poet_id: int) -> None:
    _require_poet(poet_id)
    try:
        poet_repo.delete(poet_id)
    except Exception as exc:
        raise BadRequest("删除被数据库规则拦截: " + mysql_error_message(exc)) from exc


# ---------------- 诗歌 ----------------


def _poem_payload(data: dict) -> dict:
    title = text_value(data, "title")
    if title is None or not title.strip():
        raise BadRequest("诗歌标题不能为空")

    content = text_value(data, "content")
    if content is None or not content.strip():
        raise BadRequest("诗歌正文不能为空")

    poet_id = int_value(data, "poetId")
    if poet_id is None or poet_repo.count_by_id(poet_id) == 0:
        raise NotFound(f"诗人不存在: id={_java_id(poet_id)}")

    return {
        "title": title,
        "content": content,
        "createYear": int_value(data, "createYear"),
        "form": text_value(data, "form"),
        "appreciation": text_value(data, "appreciation"),
        "poetId": poet_id,
    }


def add_poem(data: dict) -> dict:
    poem = _poem_payload(data)
    poem_id = poem_repo.insert_poem(
        poem["title"],
        poem["content"],
        poem["createYear"],
        poem["form"],
        poem["appreciation"],
        poem["poetId"],
    )
    return {"poemId": poem_id}


def update_poem(poem_id: int, data: dict) -> None:
    poem = _poem_payload(data)
    _require_poem(poem_id)
    poem_repo.update_poem(
        poem_id,
        poem["title"],
        poem["content"],
        poem["createYear"],
        poem["form"],
        poem["appreciation"],
        poem["poetId"],
    )


def change_publication_status(poem_id: int, status: str | None) -> None:
    if status not in {"published", "withdrawn"}:
        raise BadRequest("发布状态只能是 published 或 withdrawn")
    _require_poem(poem_id)
    poem_repo.update_publication_status(poem_id, status)


def delete_poem(poem_id: int) -> None:
    try:
        rowcount = poem_repo.delete_poem(poem_id)
        if rowcount == 0:
            raise NotFound(f"诗歌不存在: id={poem_id}")
    except NotFound:
        raise
    except Exception as exc:
        raise BadRequest(
            "删除被数据库规则拦截(存在评分/评论/收藏等关联记录, 请改用下架): "
            + mysql_error_message(exc)
        ) from exc


# ---------------- 诗集 ----------------


def list_collections() -> list[dict]:
    return collection_repo.list_catalog()


def _collection_payload(data: dict) -> dict:
    title = text_value(data, "title")
    if title is None or not title.strip():
        raise BadRequest("诗集名称不能为空")

    poem_ids = text_value(data, "poemIds")
    if poem_ids is None:
        poem_ids = ""

    return {
        "title": title,
        "publishYear": int_value(data, "publishYear"),
        "publisher": text_value(data, "publisher"),
        "isbn": text_value(data, "isbn"),
        "introduction": text_value(data, "introduction"),
        "poemIds": poem_ids,
    }


def add_collection(data: dict) -> None:
    collection = _collection_payload(data)
    try:
        collection_repo.add_with_poems(
            collection["title"],
            collection["publishYear"],
            collection["publisher"],
            collection["isbn"],
            collection["introduction"],
            collection["poemIds"],
        )
    except Exception as exc:
        raise BadRequest(
            "诗集创建失败(已整体回滚): " + mysql_error_message(exc)
        ) from exc


def update_collection(collection_id: int, data: dict) -> None:
    collection = _collection_payload(data)
    _require_collection(collection_id)
    collection_repo.update(
        collection_id,
        collection["title"],
        collection["publishYear"],
        collection["publisher"],
        collection["isbn"],
        collection["introduction"],
    )


def delete_collection(collection_id: int) -> None:
    _require_collection(collection_id)
    collection_repo.delete(collection_id)


# ---------------- 流派 ----------------


def add_genre(data: dict) -> dict:
    name = text_value(data, "name")
    if name is None or not name.strip():
        raise BadRequest("流派名称不能为空")

    try:
        genre_id = genre_repo.insert(name, text_value(data, "description"))
    except Exception as exc:
        if is_duplicate_error(exc):
            raise BadRequest("流派名称已存在") from exc
        raise
    return {"genreId": genre_id}


def update_genre(genre_id: int, data: dict) -> None:
    name = text_value(data, "name")
    if name is None or not name.strip():
        raise BadRequest("流派名称不能为空")

    _require_genre(genre_id)
    try:
        genre_repo.update(genre_id, name, text_value(data, "description"))
    except Exception as exc:
        if is_duplicate_error(exc):
            raise BadRequest("流派名称已存在") from exc
        raise


def delete_genre(genre_id: int) -> None:
    _require_genre(genre_id)
    genre_repo.delete(genre_id)


# ---------------- 存在性检查 ----------------


def _require_poet(poet_id: int) -> None:
    if poet_repo.count_by_id(poet_id) == 0:
        raise NotFound(f"诗人不存在: id={poet_id}")


def _require_poem(poem_id: int) -> None:
    if poem_repo.count_poem(poem_id) == 0:
        raise NotFound(f"诗歌不存在: id={poem_id}")


def _require_collection(collection_id: int) -> None:
    if collection_repo.count_by_id(collection_id) == 0:
        raise NotFound(f"诗集不存在: id={collection_id}")


def _require_genre(genre_id: int) -> None:
    if genre_repo.count_by_id(genre_id) == 0:
        raise NotFound(f"流派不存在: id={genre_id}")
