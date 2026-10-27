# Django 服务端

这是原 Spring Boot 后端的 Django 重写版本，保留原有 33 个接口、统一响应格式、业务规则和 MySQL 数据库对象。重构完成后原 Java `backend/` 目录已移除，当前仓库只保留本目录。数据库仍然是项目根目录 `sql/01`—`sql/08` 初始化的 `poetry_db`，不新增框架表，也不需要执行 Django migration。

## 技术栈

| 组件 | 选择 |
| --- | --- |
| Python | 3.11+（本机 3.13.2） |
| Web 框架 | Django 5.2 LTS |
| 数据库驱动 | PyMySQL（通过 `pymysql.install_as_MySQLdb()` 接入 Django MySQL 后端） |
| 密码哈希 | `bcrypt`，兼容种子数据中的 `$2a$10$` 哈希 |
| 会话 | 签名 Cookie，Cookie 名保持 `JSESSIONID` |
| 环境管理 | uv |

## 目录结构

```
backend_django/
├── pyproject.toml / uv.lock
├── manage.py
├── poetry_backend/
│   ├── settings.py            # 数据库、会话、CORS、日志
│   ├── urls.py                # /api/ 入口
│   └── wsgi.py / asgi.py
├── api/
│   ├── urls.py                # 33 个接口路由
│   ├── common.py              # 统一响应/分页/JSON/类型转换
│   ├── exceptions.py          # 400/401/403/404/500 异常
│   ├── decorators.py          # api_view / require_login / require_admin
│   ├── middleware.py          # CORS + OPTIONS
│   ├── db.py                  # 原生 SQL 执行与 MySQL 错误处理
│   ├── repositories/          # 每个模块一份手写 SQL
│   ├── services/              # 业务规则
│   └── views/                 # 薄视图与路由处理
└── scripts/
    ├── init_test_db.sh        # 生成独立测试库 poetry_db_test
    └── smoke_test.py          # 33 接口端到端回归
```

## 快速开始

### 1. 初始化数据库

与原 Java 版完全相同，在项目根目录执行 `sql/01`—`sql/08`（或 `01_poetry_schema_mysql.sql` + 后续脚本）：

```bash
mysql -u root -p --default-character-set=utf8mb4 < sql/01_create_database.sql
# 依次执行 02 ... 08
```

脚本不会删除已有数据库；本地重建前需自行 `DROP DATABASE poetry_db;`。

### 2. 安装依赖

```bash
cd backend_django
uv sync
```

### 3. 配置数据库

推荐把 `.env.example` 复制为 `.env` 后填写（`.env` 已被 gitignore，由 `python-dotenv` 自动加载）：

```bash
cp .env.example .env
# 编辑 .env，至少填写 DB_PASSWORD
```

也可以通过环境变量配置，不把密码写进仓库：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DB_NAME` | `poetry_db` | 数据库名 |
| `DB_USER` | `root` | 用户名 |
| `DB_PASSWORD` | `CHANGE_ME` | 必填，本地真实密码 |
| `DB_HOST` | `127.0.0.1` | MySQL 地址 |
| `DB_PORT` | `3306` | MySQL 端口 |
| `DJANGO_SECRET_KEY` | 开发占位值 | 生产环境必须替换 |
| `DJANGO_DEBUG` | `1` | 生产环境设为 `0` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,testserver` | 逗号分隔 |
| `SQL_DEBUG` | `0` | 设为 `1` 打印 SQL |

Git Bash：

```bash
export DB_PASSWORD='你的密码'
uv run python manage.py runserver 8080
```

PowerShell：

```powershell
$env:DB_PASSWORD = "你的密码"
uv run python manage.py runserver 8080
```

启动后接口地址与原 Java 版一致：`http://localhost:8080/api/...`。种子账户：`admin/admin123`、`reader1/reader123`、`reader2/reader123`。

> 不需要执行 `python manage.py migrate`。Django 只负责 HTTP、会话和业务编排，数据访问全部是手写 SQL。

## 测试

回归测试使用独立的 `poetry_db_test`，脚本会先删除并重建该库，不触碰 `poetry_db`：

```bash
cd backend_django
export DB_PASSWORD='你的密码'

bash scripts/init_test_db.sh
DB_NAME=poetry_db_test uv run python scripts/smoke_test.py
```

当前结果：**289/289 项断言通过**，覆盖公开检索、详情、全文检索、流派、注册/登录/me/登出、收藏、评分、评论、权限分支、管理端四类 CRUD、下架/恢复、触发器与外键拦截、CORS 预检和 Cookie 名。

## 与原 Java 实现的对应关系（历史对照）

| 原 Java 实现（已移除） | Django |
| --- | --- |
| `controller/*.java` | `api/views/*.py` |
| `service/*.java` | `api/services/*.py` |
| `mapper/*.java` + `mapper/*.xml` | `api/repositories/*.py`（手写参数化 SQL） |
| `common/ApiResponse` / `PageResult` | `api/common.py` |
| `common/GlobalExceptionHandler` | `api/decorators.py` 的 `api_view` + `api/exceptions.py` |
| `config/AuthInterceptor` + `@RequireLogin/@RequireAdmin` | `api/decorators.py` 的 `require_login` / `require_admin` |
| `config/WebConfig` 的 CORS | `api/middleware.py` |
| `application.yml` + `application-local.yml`（已移除） | `.env` / 环境变量 + `poetry_backend/settings.py` |
| BCryptPasswordEncoder | `bcrypt.hashpw` / `bcrypt.checkpw` |
| HttpSession / JSESSIONID | Django signed-cookie session，Cookie 名仍为 `JSESSIONID` |

数据库对象的使用位置：

- 视图：`v_poem_detail`（详情）、`v_collection_catalog`（诗集目录）；
- 存储过程：`sp_register_user`（注册）、`sp_fulltext_search_poems`（全文检索）、`sp_add_collection_with_poems`（事务式新建诗集）；
- 触发器：`trg_poet_bd`（删除有作品的诗人）、`trg_app_user_bd`、`trg_rating_bi/bu`；
- 约束：UNIQUE、CHECK、外键 RESTRICT/CASCADE 全部保留。

## 关键行为说明

1. **统一响应**：`{"code":200,"message":"success","data":...}`；分页为 `{total,page,pageSize,list}`。
2. **HTTP 状态与原版一致**：登录/管理员拦截返回 HTTP 401/403；业务异常（如诗歌不存在、评论非属主）返回 HTTP 200，body 里的 `code` 为 400/403/404。
3. **会话**：登录后下发 HttpOnly `JSESSIONID`，30 分钟过期；角色在登录时写入签名 Cookie。
4. **CSRF/CORS**：与原前端调用方式一致，接口不要求 CSRF token；CORS 仅放行 `http://localhost:5173` 和 `http://localhost:3000`，允许携带 Cookie。
5. **密码**：新注册用户使用 BCrypt（cost 10），种子 `$2a$` 哈希可直接校验；两种实现生成的哈希互相兼容。

## 与原 Java 实现的已知边界差异（历史对照）

- 缺少必填查询参数（如全文检索的 `keyword`、评分的 `score`）或 JSON 格式错误时，Django 版返回可读的 `code=400`；原 Java 版由兜底异常处理返回 `code=500` 和 Spring 的英文异常信息。正常业务路径不受影响。
- 注销使用签名 Cookie 的删除，浏览器端立即失效；原 Java 版是服务端 HttpSession 失效。两者对正常前端行为一致，但已复制到其他客户端的旧 Cookie 在 Django 版中会保留到 30 分钟过期。
- Django 版不启用 Django Admin/Auth，不生成 `django_session` 等框架表；课程数据库结构保持 10 张表不变。

## 常见问题

- **MySQL 版本**：需要 8.0.16+（CHECK 约束强制生效、ngram 全文索引）。本机实测 MySQL 9.7.1。
- **中文乱码**：初始化时带 `--default-character-set=utf8mb4`；Django 连接已设置 `charset=utf8mb4`。
- **PyMySQL 认证失败**：MySQL 8+ 默认 `caching_sha2_password`，项目已通过 `pymysql[rsa]` 安装 `cryptography`。
- **端口占用**：`runserver 8080` 与原 Java 版相同；如 8080 被占用可改用其他端口，前端 `baseURL` 同步调整。
- **测试库安全**：`init_test_db.sh` 只允许数据库名以 `_test` 结尾，并会 `DROP DATABASE` 后重建；不要把它指向 `poetry_db`。
