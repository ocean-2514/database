# Django 重构计划

> 状态：已完成。当前分支只保留 Django 服务端 `backend_django/`，原 Java `backend/` 已移除。
>
> 重构目标：在保留 `align` 分支现有功能、HTTP 契约和 MySQL 数据库对象的前提下，用 Django 重写原 Spring Boot + MyBatis 服务端。
>
> 基线：`align` 分支（33 个接口、10 张表、3 个视图、4 个触发器、4 个存储过程）。新分支：`django-rewrite`。

## 1. 范围与原则

### 1.1 保持不变

1. **接口契约**：33 个接口的路径、HTTP 方法、查询参数、JSON 字段名（camelCase）不变。
2. **统一响应**：`{"code": ..., "message": ..., "data": ...}`；分页结构 `{total, page, pageSize, list}`。
3. **业务规则**：注册校验、BCrypt 密码、登录/停用账户、收藏防重、评分覆盖写、评论属主校验、管理员权限、下架语义等。
4. **数据库设计**：继续使用现有 `sql/01`—`sql/08` 初始化的 `poetry_db`；视图、触发器、存储过程仍然参与业务，不改为纯 ORM 实现。
5. **错误提示**：已有中文提示和业务错误码尽量逐字保留。
6. **Cookie 会话**：登录后仍以 HttpOnly Cookie 维持会话，前端无需改成 Token。

### 1.2 明确不做

- 不重写前端（仓库中只有后端；原架构文档里的 `frontend/` 仍是“建设中”）。
- 不修改数据库表结构、字段名、枚举值、索引和 SQL 脚本。
- 不引入 Django Admin、Django Auth 用户表或迁移文件；避免往课程数据库中增加框架表。
- 不把原生 SQL 全部改成 ORM；课程项目中的 SQL / 视图 / 存储过程仍需可讲解、可演示。

## 2. 技术选型

| 层 | 原 Java 实现 | Django 实现 |
| --- | --- | --- |
| Web 框架 | 原 Spring Boot 3.3.5 | Django 5.2 LTS |
| 路由/参数绑定 | Controller + 注解 | `api/urls.py` + 函数视图 |
| 权限拦截 | `AuthInterceptor` + 注解 | `api/decorators.py` 装饰器 |
| 业务层 | `service/*.java` | `api/services/*.py` |
| 数据访问 | 原 MyBatis Mapper XML | `api/repositories/*.py` 手写 SQL |
| 事务/存储过程 | 原 MyBatis `CALL` | `cursor.callproc`/`CALL` + 原生 SQL |
| 密码哈希 | 原 Spring BCrypt | `bcrypt` 包（兼容 `$2a$` 旧哈希） |
| 会话 | HttpSession(JSESSIONID) | Django signed-cookie session，Cookie 名设为 `JSESSIONID` |
| 统一异常 | `GlobalExceptionHandler` | `api/exceptions.py` + `@api_view` |
| 构建 | Maven | uv + `pyproject.toml` |
| 驱动 | MySQL Connector/J | PyMySQL（`pymysql.install_as_MySQLdb()`） |

## 3. 目录结构

```
backend_django/
├── pyproject.toml / uv.lock          # uv 管理
├── manage.py
├── poetry_backend/
│   ├── __init__.py                   # PyMySQL 适配
│   ├── settings.py                   # 数据库/会话/CORS/日志
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── api/
│   ├── urls.py                       # 33 个路由
│   ├── common.py                     # 响应、分页、JSON、类型转换
│   ├── exceptions.py                 # ApiError / 400 / 401 / 403 / 404
│   ├── decorators.py                 # api_view / require_login / require_admin
│   ├── middleware.py                 # CORS + OPTIONS
│   ├── db.py                         # 连接、字典游标、Decimal 转换
│   ├── repositories/                 # 每个模块一份手写 SQL
│   ├── services/                     # 业务规则
│   └── views/                        # 薄视图
├── scripts/
│   ├── init_test_db.sh               # 从 sql/ 生成 poetry_db_test
│   └── smoke_test.py                 # 33 接口端到端回归
└── README.md
```

`backend_django/` 是当前唯一保留的服务端；原 Java `backend/` 已在重构完成后删除，仅存在于 git 历史中。

## 4. 实施步骤

### 阶段 0：基线与分支（已完成）

- 通读 Controller / Service / Mapper XML / SQL / 文档。
- 从 `align` 创建 `django-rewrite`。
- 记录 33 个接口的请求、响应字段和错误提示。

### 阶段 1：项目骨架

1. 在 `backend_django/` 写 `pyproject.toml`，使用 `uv sync` 安装 Django 5.2、PyMySQL[rsa]、bcrypt。
2. 创建 Django 工程与 `api` 应用。
3. 配置 MySQL：`DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT` 环境变量，默认端口 8080。
4. 配置 signed-cookie session、`JSESSIONID` Cookie 名、30 分钟过期、HttpOnly。
5. 关闭 CSRF（保持原前端无 token 的调用方式），实现限定 `localhost:5173/3000` 的 CORS 与 OPTIONS 预检。

### 阶段 2：公共基础设施

1. `ApiResponse` / `PageResult` 等价实现，保证 JSON 字段名与顺序。
2. 全局异常转换：
   - 参数/业务校验 → body `code=400`；
   - 未登录 → HTTP 401 + `code=401`；
   - 非管理员 → HTTP 403 + `code=403`；
   - 资源不存在 → body `code=404`；
   - 未知异常 → body `code=500`。
   - 与原实现保持一致：除登录/角色拦截外，业务错误 HTTP 状态仍为 200。
3. 分页归一：页码最小 1；页大小默认 10、上限 50。
4. JSON 解析：camelCase 入参、`ensure_ascii=False`、Decimal→float、datetime→ISO 8601。
5. 原生 SQL 工具：字典行、参数绑定、MySQL SIGNAL/FK/UNIQUE 错误消息提取。

### 阶段 3：公开接口

1. `GET /api/poems`：动态 WHERE（keyword/poetName/genre/yearFrom/yearTo）、COUNT + LIMIT、三种排序。
2. `GET /api/poems/fulltext`：调用 `sp_fulltext_search_poems`。
3. `GET /api/poems/{id}`：查询 `v_poem_detail`，未发布/不存在返回 404。
4. `GET /api/genres`。

### 阶段 4：认证

1. 注册：长度/邮箱格式校验 → 用户名预查重 → `bcrypt.hashpw` → `sp_register_user`。
2. 登录：数据库排序规则下的大小写不敏感查询、BCrypt `checkpw`、停用账户拒绝、写入 session。
3. `GET /api/auth/me`、`POST /api/auth/logout`。

### 阶段 5：用户互动

1. 收藏：已发布校验、防重、默认类型“默认”、分页列表（只显示已发布）。
2. 评分：1–5、已发布校验、`ON DUPLICATE KEY UPDATE`、created/updated 判定。
3. 评论：内容 trim/1–1000 字、已发布校验、分页、属主/管理员权限。

### 阶段 6：管理端

1. 诗人：列表、新增、修改、删除；删除被触发器拦截时转 400。
2. 诗歌：新增、修改、下架/恢复、物理删除（RESTRICT 转 400）。
3. 诗集：目录列表（`v_collection_catalog`）、事务存储过程新增、修改、删除。
4. 流派：新增/修改/删除；UNIQUE 重名转 400。

### 阶段 7：测试与验证

1. `scripts/init_test_db.sh` 将 `sql/01`—`sql/08` 中的库名替换为 `poetry_db_test` 后执行，避免污染现有 `poetry_db`。
2. `scripts/smoke_test.py` 使用 Django test client 覆盖：
   - 公开检索/详情/全文/流派；
   - 注册/重复注册/登录/错误密码/停用账户/me/logout；
   - 收藏、评分、评论的正常流程与重复/越权/未登录分支；
   - 管理端 4 类 CRUD、下架、触发器拦截、外键拦截；
   - 响应字段、分页字段、错误码断言。
3. `uv run python manage.py check`。
4. 在 MySQL 9.7.1 上跑通全部测试，并抽查与原实现响应的字段一致性。

### 阶段 8：文档

1. `backend_django/README.md`：uv 安装、数据库初始化、环境变量、启动、测试、接口映射。
2. 根 `README.md` 改为 Django 单后端口径，删除 Java 启动说明。
3. 记录与原实现的已知差异（例如缺参时的 400/500 边界、JSON 解析报错文案）。

## 5. 关键兼容点

| 风险点 | 处理方式 |
| --- | --- |
| 种子密码是 `$2a$` BCrypt | 直接用 `bcrypt.checkpw`，新注册也用 BCrypt，原 Java 仍可校验 |
| 评分 `created/updated` 依赖 MySQL 受影响行数 | 保留 `ON DUPLICATE KEY UPDATE`，按 rowcount 判定 |
| 视图/存储过程依赖 MySQL 8.0.16+ | 启动文档明确版本要求；测试库用同一套 SQL |
| 用户名/邮箱大小写不敏感 | 依赖数据库 `utf8mb4_0900_ai_ci`，不在 Python 层额外 lower |
| 分页上限 | 严格按原实现：默认 10、上限 50 |
| 无效 JSON/缺参数 | 返回可读 400；记录为与原实现的边界差异 |
| CORS + Cookie | 仅放行 localhost:5173/3000，`allow_credentials=true`，关闭 CSRF |
| 不增加框架表 | 使用 signed-cookie session，不执行 `migrate` |

## 6. 验收标准

- 33 个接口全部可调用，成功响应字段与原实现一致。
- 种子账户 `admin/admin123`、`reader1/reader123`、`reader2/reader123` 可登录。
- 触发器、存储过程、视图仍被实际调用。
- 未登录 401、非管理员 403、属主校验 403、资源不存在 404 与原实现一致。
- `uv run python scripts/smoke_test.py` 全部通过。
- Java 后端目录已移除，Django 版本可独立启动。
