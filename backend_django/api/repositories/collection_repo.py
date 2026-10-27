"""诗集读写，新建诗集使用事务存储过程。"""
from ..db import call_procedure, execute, fetch_all, fetch_scalar


def list_catalog() -> list[dict]:
    rows = fetch_all(
        """
        SELECT collection_id AS collectionId,
               collection_name AS title,
               publication_year AS publishYear,
               publisher,
               isbn,
               description AS introduction,
               poem_count AS poemCount
        FROM v_collection_catalog
        ORDER BY collection_id
        """
    )
    # 与原实体保持一致：列表接口也会输出 poemIds=null
    for row in rows:
        row["poemIds"] = None
    return rows


def count_by_id(collection_id: int) -> int:
    return int(
        fetch_scalar(
            "SELECT COUNT(*) AS total FROM poetry_collection WHERE collection_id = %s",
            [collection_id],
        )
    )


def add_with_poems(
    title,
    publish_year,
    publisher,
    isbn,
    introduction,
    poem_ids: str,
) -> None:
    call_procedure(
        """
        CALL sp_add_collection_with_poems(%s, %s, %s, %s, %s, %s)
        """,
        [title, publish_year, publisher, isbn, introduction, poem_ids],
    )


def update(collection_id, title, publish_year, publisher, isbn, introduction) -> int:
    rowcount, _ = execute(
        """
        UPDATE poetry_collection
        SET collection_name = %s,
            publication_year = %s,
            publisher = %s,
            isbn = %s,
            description = %s
        WHERE collection_id = %s
        """,
        [title, publish_year, publisher, isbn, introduction, collection_id],
    )
    return rowcount


def delete(collection_id: int) -> int:
    rowcount, _ = execute(
        "DELETE FROM poetry_collection WHERE collection_id = %s", [collection_id]
    )
    return rowcount
