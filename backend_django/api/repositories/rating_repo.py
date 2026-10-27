"""评分记录读写。"""
from ..db import execute, fetch_one


def find_by_user_and_poem(user_id: int, poem_id: int) -> dict | None:
    return fetch_one(
        """
        SELECT rating_id AS ratingId,
               user_id AS userId,
               poem_id AS poemId,
               score,
               rated_at AS ratingTime
        FROM poem_rating
        WHERE user_id = %s AND poem_id = %s
        """,
        [user_id, poem_id],
    )


def upsert(user_id: int, poem_id: int, score: int) -> int:
    """首次评分 INSERT；再次评分命中 UNIQUE 后改为 UPDATE。"""
    rowcount, _ = execute(
        """
        INSERT INTO poem_rating (user_id, poem_id, score)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            score = %s,
            rated_at = CURRENT_TIMESTAMP
        """,
        [user_id, poem_id, score, score],
    )
    return rowcount


def delete_rating(user_id: int, poem_id: int) -> int:
    rowcount, _ = execute(
        "DELETE FROM poem_rating WHERE user_id = %s AND poem_id = %s",
        [user_id, poem_id],
    )
    return rowcount
