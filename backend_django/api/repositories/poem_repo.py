"""诗歌检索、详情、全文检索与管理端写操作。"""
from ..db import call_procedure, execute, fetch_all, fetch_one, fetch_scalar

_SEARCH_FROM = """
FROM poem p
JOIN poet pt ON pt.poet_id = p.poet_id
"""

_SEARCH_COLUMNS = """
SELECT p.poem_id AS poemId,
       p.title,
       pt.name AS poetName,
       p.creation_year AS createYear,
       p.poem_form AS form,
       CHAR_LENGTH(p.content) AS wordCount,
       IFNULL((SELECT ROUND(AVG(r.score), 1)
                 FROM poem_rating r
                WHERE r.poem_id = p.poem_id), 0) AS avgScore,
       (SELECT COUNT(*) FROM poem_rating r   WHERE r.poem_id = p.poem_id) AS ratingCount,
       (SELECT COUNT(*) FROM poem_comment c  WHERE c.poem_id = p.poem_id) AS commentCount,
       (SELECT COUNT(*) FROM poem_favorite f WHERE f.poem_id = p.poem_id) AS favoriteCount
"""


def _search_condition(keyword, poet_name, genre, year_from, year_to):
    clauses = ["p.publication_status = 'published'"]
    params: list = []

    if keyword:
        clauses.append("(p.title LIKE %s OR p.content LIKE %s)")
        like = f"%{keyword}%"
        params.extend([like, like])
    if poet_name:
        clauses.append("pt.name LIKE %s")
        params.append(f"%{poet_name}%")
    if year_from is not None:
        clauses.append("p.creation_year >= %s")
        params.append(year_from)
    if year_to is not None:
        clauses.append("p.creation_year <= %s")
        params.append(year_to)
    if genre:
        clauses.append(
            """p.poem_id IN (
                   SELECT pg.poem_id
                     FROM poem_genre pg
                     JOIN genre g ON g.genre_id = pg.genre_id
                    WHERE g.genre_name LIKE %s
               )"""
        )
        params.append(f"%{genre}%")

    return " WHERE " + " AND ".join(clauses), params


def count_poems(keyword, poet_name, genre, year_from, year_to) -> int:
    where, params = _search_condition(keyword, poet_name, genre, year_from, year_to)
    return int(fetch_scalar("SELECT COUNT(*) AS total " + _SEARCH_FROM + where, params))


def search_poems(keyword, poet_name, genre, year_from, year_to, order_by, offset, limit):
    where, params = _search_condition(keyword, poet_name, genre, year_from, year_to)
    if order_by == 1:
        order = " ORDER BY avgScore DESC, p.poem_id DESC"
    elif order_by == 2:
        order = " ORDER BY p.title ASC"
    else:
        order = " ORDER BY p.poem_id DESC"

    sql = _SEARCH_COLUMNS + _SEARCH_FROM + where + order + " LIMIT %s OFFSET %s"
    return fetch_all(sql, [*params, limit, offset])


def get_poem_detail(poem_id: int) -> dict | None:
    return fetch_one(
        """
        SELECT poem_id AS poemId,
               title,
               content,
               creation_year AS createYear,
               poem_form AS form,
               word_count AS wordCount,
               appreciation,
               poet_id AS poetId,
               poet_name AS poetName,
               pen_name AS penName,
               birth_year AS birthYear,
               death_year AS deathYear,
               genres,
               avg_score AS avgScore,
               comment_count AS commentCount,
               favorite_count AS favoriteCount
        FROM v_poem_detail
        WHERE poem_id = %s
        """,
        [poem_id],
    )


def count_published_poem(poem_id: int) -> int:
    return int(
        fetch_scalar(
            "SELECT COUNT(*) AS total FROM poem "
            "WHERE poem_id = %s AND publication_status = 'published'",
            [poem_id],
        )
    )


def count_poem(poem_id: int) -> int:
    return int(
        fetch_scalar("SELECT COUNT(*) AS total FROM poem WHERE poem_id = %s", [poem_id])
    )


def fulltext_search(keyword: str) -> list[dict]:
    rows = call_procedure("CALL sp_fulltext_search_poems(%s)", [keyword])
    return [
        {
            "poemId": row["poem_id"],
            "title": row["title"],
            "createYear": row["create_year"],
            "relevance": row["relevance"],
        }
        for row in rows
    ]


# ---------------- 管理端 ----------------


def insert_poem(title, content, create_year, form, appreciation, poet_id) -> int:
    _, poem_id = execute(
        """
        INSERT INTO poem (title, content, creation_year, poem_form, appreciation, poet_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        [title, content, create_year, form, appreciation, poet_id],
    )
    return int(poem_id)


def update_poem(poem_id, title, content, create_year, form, appreciation, poet_id) -> int:
    rowcount, _ = execute(
        """
        UPDATE poem
        SET title = %s,
            content = %s,
            creation_year = %s,
            poem_form = %s,
            appreciation = %s,
            poet_id = %s
        WHERE poem_id = %s
        """,
        [title, content, create_year, form, appreciation, poet_id, poem_id],
    )
    return rowcount


def update_publication_status(poem_id: int, status: str) -> int:
    rowcount, _ = execute(
        "UPDATE poem SET publication_status = %s WHERE poem_id = %s",
        [status, poem_id],
    )
    return rowcount


def delete_poem(poem_id: int) -> int:
    rowcount, _ = execute("DELETE FROM poem WHERE poem_id = %s", [poem_id])
    return rowcount
