"""Django settings for the poetry management system.

数据库仍使用项目根目录 sql/01-08 初始化的 poetry_db。
所有业务 SQL 都是手写原生 SQL，因此不定义 Django model、不生成迁移。
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "dev-only-secret-key-change-me-in-production",
)
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.sessions",
    "api",
]

MIDDLEWARE = [
    "api.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "poetry_backend.urls"
TEMPLATES = []
WSGI_APPLICATION = "poetry_backend.wsgi.application"
ASGI_APPLICATION = "poetry_backend.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "poetry_db"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", "CHANGE_ME"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
        "ATOMIC_REQUESTS": False,
        "TEST": {
            "NAME": os.getenv("DB_TEST_NAME", "poetry_db_test"),
        },
    }
}

# 使用签名 Cookie 保存会话，避免在课程数据库中额外创建 django_session 表；
# Cookie 名保持与原实现一致的 JSESSIONID。
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_NAME = "JSESSIONID"
SESSION_COOKIE_AGE = 30 * 60
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)

# 原前端以跨域 + Cookie 方式调用，接口不携带 CSRF token。
# 因此不启用 CsrfViewMiddleware，由视图统一 csrf_exempt。
APPEND_SLASH = False

# 诗歌正文可能较长；默认 2.5MB 对课程数据足够，这里放宽到 10MB。
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = False
USE_TZ = False
DEFAULT_CHARSET = "utf-8"

# 不运行 migrate；sessions 使用 signed cookies，不需要数据库迁移。
MIGRATION_MODULES = {"sessions": None}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "api": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG" if env_bool("SQL_DEBUG", False) else "WARNING",
            "propagate": False,
        },
    },
}
