"""评论读写。"""
from ..db import execute, fetch_all, fetch_one, fetch_scalar


def find_by_comment_id(comment_id: int) -> dict | None:
    return fetch_one(
        """
        SELECT comment_id AS commentId,
               user_id AS userId,
               poem_id AS poemId,
               content,
               created_at AS commentTime,
               like_count AS likeCount
        FROM poem_comment
        WHERE comment_id = %s
        """,
        [comment_id],
    )


def list_by_poem(poem_id: int, offset: int, limit: int) -> list[dict]:
    return fetch_all(
        """
        SELECT c.comment_id AS commentId,
               u.username,
               c.content,
               c.like_count AS likeCount,
               c.created_at AS commentTime
        FROM poem_comment c
        JOIN app_user u ON u.user_id = c.user_id
        WHERE c.poem_id = %s
        ORDER BY c.created_at DESC, c.comment_id DESC
        LIMIT %s OFFSET %s
        """,
        [poem_id, limit, offset],
    )


def count_by_poem(poem_id: int) -> int:
    return int(
        fetch_scalar(
            "SELECT COUNT(*) AS total FROM poem_comment WHERE poem_id = %s",
            [poem_id],
        )
    )


def insert_comment(user_id: int, poem_id: int, content: str) -> int:
    _, comment_id = execute(
        "INSERT INTO poem_comment (user_id, poem_id, content) VALUES (%s, %s, %s)",
        [user_id, poem_id, content],
    )
    return int(comment_id)


def update_content(comment_id: int, content: str) -> int:
    rowcount, _ = execute(
        "UPDATE poem_comment SET content = %s WHERE comment_id = %s",
        [content, comment_id],
    )
    return rowcount


def delete_comment(comment_id: int) -> int:
    rowcount, _ = execute("DELETE FROM poem_comment WHERE comment_id = %s", [comment_id])
    return rowcount
