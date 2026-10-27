"""认证业务：注册、登录、当前用户、登出。

密码哈希保持 BCrypt，因此 sql/07_seed_data.sql 里的 $2a$10$ 种子哈希
和原实现生成的哈希都能继续使用。
"""
import re

import bcrypt

from ..common import text_value
from ..exceptions import ApiError, BadRequest
from ..repositories import auth_repo

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# jBCrypt 按 72 字节截断；bcrypt 5.x 对超长输入直接报错，这里显式截断。
_BCRYPT_MAX_BYTES = 72


def _password_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def _user_view(user: dict) -> dict:
    return {
        "userId": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "status": user["status"],
        "registerTime": user["register_time"],
    }


def register(data: dict) -> dict:
    username = (text_value(data, "username") or "").strip()
    if not (2 <= len(username) <= 30):
        raise BadRequest("用户名长度需为 2-30 个字符")

    password = text_value(data, "password") or ""
    if not (6 <= len(password) <= 64):
        raise BadRequest("密码长度需为 6-64 个字符")

    email = (text_value(data, "email") or "").strip()
    if not email:
        raise BadRequest("邮箱不能为空")
    if not _EMAIL_RE.match(email):
        raise BadRequest("邮箱格式不正确")

    if auth_repo.find_user_by_username(username) is not None:
        raise BadRequest("用户名已存在")

    password_hash = bcrypt.hashpw(
        _password_bytes(password), bcrypt.gensalt(rounds=10)
    ).decode("ascii")

    try:
        auth_repo.register_user(username, password_hash, email)
    except Exception as exc:  # 存储过程 SIGNAL：用户名或邮箱已存在
        raise BadRequest("用户名或邮箱已存在") from exc

    user = auth_repo.find_user_by_username(username)
    if user is None:
        raise ApiError("注册成功但无法读取用户信息", code=500)
    return _user_view(user)


def login(data: dict, request) -> dict:
    username = (text_value(data, "username") or "").strip()
    password = text_value(data, "password") or ""

    user = auth_repo.find_user_by_username(username)
    password_ok = False
    if user is not None:
        try:
            password_ok = bcrypt.checkpw(
                _password_bytes(password), user["password_hash"].encode("utf-8")
            )
        except ValueError:
            password_ok = False

    # 用户不存在与密码错误使用同一提示，避免枚举用户名
    if user is None or not password_ok:
        raise BadRequest("用户名或密码错误")
    if user["status"] == "disabled":
        raise BadRequest("账户已被停用")

    request.session["userId"] = user["user_id"]
    request.session["username"] = user["username"]
    request.session["role"] = user["role"]
    return _user_view(user)


def current_user(request) -> dict | None:
    user_id = request.session.get("userId")
    if user_id is None:
        return None
    user = auth_repo.find_user_by_id(user_id)
    return None if user is None else _user_view(user)


def logout(request) -> None:
    request.session.flush()
