#!/usr/bin/env bash
# 初始化独立的接口测试库：把 sql/01-08 中的 poetry_db 替换为 poetry_db_test。
# 不会修改或删除现有的 poetry_db。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

DB="${TEST_DB_NAME:-poetry_db_test}"
if [[ ! "$DB" =~ ^[A-Za-z0-9_]+$ ]]; then
  echo "拒绝执行：测试库名只能包含字母、数字和下划线（当前：$DB）" >&2
  exit 1
fi
if [[ "$DB" != *_test ]]; then
  echo "拒绝执行：测试库名必须以 _test 结尾（当前：$DB）" >&2
  exit 1
fi
if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "请先设置 DB_PASSWORD 环境变量" >&2
  exit 1
fi

export MYSQL_PWD="$DB_PASSWORD"
MYSQL=(mysql -u "${DB_USER:-root}" --default-character-set=utf8mb4)
if [[ -n "${DB_HOST:-}" ]]; then
  MYSQL+=(-h "$DB_HOST")
fi
if [[ -n "${DB_PORT:-}" ]]; then
  MYSQL+=(-P "$DB_PORT")
fi

echo "重建测试库 $DB ..."
"${MYSQL[@]}" -e "DROP DATABASE IF EXISTS \`$DB\`;"

for file in \
  "$ROOT_DIR/sql/01_create_database.sql" \
  "$ROOT_DIR/sql/02_create_tables.sql" \
  "$ROOT_DIR/sql/03_indexes.sql" \
  "$ROOT_DIR/sql/04_views.sql" \
  "$ROOT_DIR/sql/05_triggers.sql" \
  "$ROOT_DIR/sql/06_procedures.sql" \
  "$ROOT_DIR/sql/07_seed_data.sql" \
  "$ROOT_DIR/sql/08_expand_data.sql"
do
  echo "  执行 $(basename "$file")"
  sed "s/poetry_db/$DB/g" "$file" | "${MYSQL[@]}"
done

echo "测试库 $DB 初始化完成。"
