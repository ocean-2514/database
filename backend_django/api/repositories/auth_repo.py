"""用户查询与注册存储过程。"""
from ..db import call_procedure_with_out, fetch_one

_USER_COLUMNS = """
SELECT user_id,
       username,
       password_hash,
       email,
       role,
       account_status AS status,
       registered_at AS register_time
FROM app_user
"""


def find_user_by_username(username: str) -> dict | None:
    return fetch_one(_USER_COLUMNS + " WHERE username = %s", [username])


def find_user_by_id(user_id: int) -> dict | None:
    return fetch_one(_USER_COLUMNS + " WHERE user_id = %s", [user_id])


def register_user(username: str, password_hash: str, email: str) -> int:
    return call_procedure_with_out(
        "CALL sp_register_user(%s, %s, %s, @poetry_new_user_id)",
        [username, password_hash, email],
        out_variable="@poetry_new_user_id",
    )
