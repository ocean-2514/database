"""诗人读写。"""
from ..db import execute, fetch_all, fetch_scalar


def list_all() -> list[dict]:
    return fetch_all(
        """
        SELECT poet_id AS poetId,
               name,
               pen_name AS penName,
               gender,
               birth_year AS birthYear,
               death_year AS deathYear,
               nationality,
               biography
        FROM poet
        ORDER BY poet_id
        """
    )


def count_by_id(poet_id: int) -> int:
    return int(fetch_scalar("SELECT COUNT(*) AS total FROM poet WHERE poet_id = %s", [poet_id]))


def insert(poet: dict) -> int:
    _, poet_id = execute(
        """
        INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        [
            poet["name"],
            poet["penName"],
            poet["gender"],
            poet["birthYear"],
            poet["deathYear"],
            poet["nationality"],
            poet["biography"],
        ],
    )
    return int(poet_id)


def update(poet_id: int, poet: dict) -> int:
    rowcount, _ = execute(
        """
        UPDATE poet
        SET name = %s,
            pen_name = %s,
            gender = %s,
            birth_year = %s,
            death_year = %s,
            nationality = %s,
            biography = %s
        WHERE poet_id = %s
        """,
        [
            poet["name"],
            poet["penName"],
            poet["gender"],
            poet["birthYear"],
            poet["deathYear"],
            poet["nationality"],
            poet["biography"],
            poet_id,
        ],
    )
    return rowcount


def delete(poet_id: int) -> int:
    rowcount, _ = execute("DELETE FROM poet WHERE poet_id = %s", [poet_id])
    return rowcount
