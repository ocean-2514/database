"""流派读写。"""
from ..db import execute, fetch_all, fetch_scalar


def list_all() -> list[dict]:
    return fetch_all(
        """
        SELECT genre_id AS genreId,
               genre_name AS name,
               description
        FROM genre
        ORDER BY genre_id
        """
    )


def count_by_id(genre_id: int) -> int:
    return int(fetch_scalar("SELECT COUNT(*) AS total FROM genre WHERE genre_id = %s", [genre_id]))


def insert(name: str, description: str | None) -> int:
    _, genre_id = execute(
        "INSERT INTO genre (genre_name, description) VALUES (%s, %s)",
        [name, description],
    )
    return int(genre_id)


def update(genre_id: int, name: str, description: str | None) -> int:
    rowcount, _ = execute(
        "UPDATE genre SET genre_name = %s, description = %s WHERE genre_id = %s",
        [name, description, genre_id],
    )
    return rowcount


def delete(genre_id: int) -> int:
    rowcount, _ = execute("DELETE FROM genre WHERE genre_id = %s", [genre_id])
    return rowcount
