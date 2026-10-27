"""收藏记录读写。"""
from ..db import execute, fetch_all, fetch_scalar


def find_user_favorite(user_id: int, poem_id: int):
    return fetch_scalar(
        "SELECT favorite_id FROM poem_favorite WHERE user_id = %s AND poem_id = %s",
        [user_id, poem_id],
    )


def insert_favorite(user_id: int, poem_id: int, favorite_type: str) -> int:
    _, favorite_id = execute(
        "INSERT INTO poem_favorite (user_id, poem_id, favorite_type) VALUES (%s, %s, %s)",
        [user_id, poem_id, favorite_type],
    )
    return int(favorite_id)


def delete_favorite(user_id: int, poem_id: int) -> int:
    rowcount, _ = execute(
        "DELETE FROM poem_favorite WHERE user_id = %s AND poem_id = %s",
        [user_id, poem_id],
    )
    return rowcount


def list_user_favorites(user_id: int, offset: int, limit: int) -> list[dict]:
    return fetch_all(
        """
        SELECT p.poem_id AS poemId,
               p.title,
               pt.name AS poetName,
               p.creation_year AS createYear,
               p.poem_form AS form,
               IFNULL((SELECT ROUND(AVG(r.score), 1)
                         FROM poem_rating r
                        WHERE r.poem_id = p.poem_id), 0) AS avgScore,
               f.favorite_type AS favoriteType,
               f.favorited_at AS favoriteTime
        FROM poem_favorite f
        JOIN poem p  ON p.poem_id  = f.poem_id
        JOIN poet pt ON pt.poet_id = p.poet_id
        WHERE f.user_id = %s
          AND p.publication_status = 'published'
        ORDER BY f.favorited_at DESC
        LIMIT %s OFFSET %s
        """,
        [user_id, limit, offset],
    )


def count_user_favorites(user_id: int) -> int:
    return int(
        fetch_scalar(
            """
            SELECT COUNT(*) AS total
            FROM poem_favorite f
            JOIN poem p ON p.poem_id = f.poem_id
            WHERE f.user_id = %s
              AND p.publication_status = 'published'
            """,
            [user_id],
        )
    )
