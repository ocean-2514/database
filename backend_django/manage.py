#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poetry_backend.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django，请先在 backend_django 目录执行 `uv sync`。"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
