# Django 重构说明

本文记录 `django-rewrite` 分支上对原 Spring Boot 后端的 Django 重写结果，便于答辩时对照讲解。重构完成后原 Java `backend/` 目录已移除，当前仓库只保留 Django 服务端。

## 1. 重构范围

- 重写对象：原 Spring Boot 后端的 33 个 HTTP 接口与全部业务规则。
- 保持不变：接口路径/方法、JSON 字段名、统一响应包装、分页语义、BCrypt 密码、MySQL 表结构、3 个视图、4 个触发器、4 个存储过程、权限与错误提示。
- 未包含：前端（仓库中没有前端代码）、Django Admin/Auth、数据库迁移。
- 重构完成后已移除 Java 后端，只保留 `backend_django/`；本文件保留 Java→Django 映射，作为重构过程说明。

## 2. 分层映射

| 原 Java 实现（已移除） | Django | 说明 |
| --- | --- | --- |
| `PoetryApplication` | `manage.py` + `poetry_backend/` | 应用入口与配置 |
| `controller/AuthController` | `api/views/auth_views.py` | 注册/登录/me/登出 |
| `controller/PoemController` | `api/views/poem_views.py` | 检索/全文检索/详情/流派 |
| `controller/FavoriteController` | `api/views/favorite_views.py` | 收藏 |
| `controller/RatingController` | `api/views/rating_views.py` | 评分 |
| `controller/CommentController` | `api/views/comment_views.py` | 评论 |
| `controller/AdminController` | `api/views/admin_views.py` | 四类管理端 CRUD |
| `service/*Service` | `api/services/*_service.py` | 校验、分页、属主/管理员权限 |
| `mapper/*Mapper.java` + `resources/mapper/*.xml` | `api/repositories/*_repo.py` | 参数化原生 SQL、视图/存储过程调用 |
| `common/ApiResponse` | `api/common.py: ok/error/json_response` | 统一响应 |
| `common/PageResult` | `api/common.py: page_result` | 分页结构 |
| `common/GlobalExceptionHandler` | `api/decorators.py: api_view` + `api/exceptions.py` | 异常转统一 JSON |
| `config/AuthInterceptor` | `api/decorators.py: require_login/require_admin` | 401/403 短路 |
| `config/WebConfig` | `api/middleware.py: CorsMiddleware` | CORS 与预检 |
| `config/SecurityConfig` | `api/services/auth_service.py` | BCrypt 10 轮 |
| `application.yml` / `application-local.yml`（已移除） | `poetry_backend/settings.py` + `.env` / 环境变量 | 数据源和外部配置 |

## 3. 数据库对象调用点

| 数据库对象 | Django 调用点 |
| --- | --- |
| `v_poem_detail` | `poem_repo.get_poem_detail` |
| `v_collection_catalog` | `collection_repo.list_catalog` |
| `v_poem_brief` | 原 Java 版未直接使用；Django 版保持不使用 |
| `sp_register_user` | `auth_repo.register_user`（OUT 参数用会话变量承接） |
| `sp_fulltext_search_poems` | `poem_repo.fulltext_search` |
| `sp_add_collection_with_poems` | `collection_repo.add_with_poems` |
| `trg_poet_bd` | 删除诗人时由 MySQL 抛 SIGNAL，`admin_service.delete_poet` 转 400 |
| `trg_rating_bi/bu` | 评分写入由 MySQL 校验，Django 不复制该规则 |
| `trg_app_user_bd` | 当前无删除用户接口；保留数据库端保护 |

## 4. 契约保持

### 4.1 响应

```json
{"code": 200, "message": "success", "data": ...}
```

分页：

```json
{"total": 12, "page": 1, "pageSize": 10, "list": [...]}
```

字段名保持 camelCase，例如：

- 列表：`poemId/title/poetName/createYear/form/wordCount/avgScore/ratingCount/commentCount/favoriteCount`
- 详情：`poemId/title/content/createYear/form/wordCount/appreciation/poetId/poetName/penName/birthYear/deathYear/genres/avgScore/commentCount/favoriteCount`
- 用户：`userId/username/email/role/status/registerTime`
- 收藏：`poemId/title/poetName/createYear/form/avgScore/favoriteType/favoriteTime`
- 评论：`commentId/username/content/likeCount/commentTime`
- 管理端诗集：`collectionId/title/publishYear/publisher/isbn/introduction/poemCount/poemIds`

### 4.2 权限与状态码

| 场景 | HTTP | body.code |
| --- | --- | --- |
| 未登录访问需登录接口 | 401 | 401 |
| 非管理员访问管理端 | 403 | 403 |
| 评论非属主修改 | 200 | 403 |
| 管理端资源不存在 | 200 | 404 |
| 参数/业务校验失败 | 200 | 400 |
| 未知异常 | 200 | 500 |

### 4.3 认证

- 种子哈希 `$2a$10$...` 用 `bcrypt.checkpw` 直接校验；
- 新注册使用 `bcrypt.hashpw(..., gensalt(rounds=10))`，原 Java 版仍可校验（历史对照）；
- 登录成功写入签名 Cookie，Cookie 名 `JSESSIONID`，HttpOnly，30 分钟过期；
- 停用账户（`account_status='disabled'`）拒绝登录。

## 5. 验证结果

在 MySQL 9.7.1 上重建独立测试库 `poetry_db_test` 后运行：

```bash
cd backend_django
DB_NAME=poetry_db_test uv run python scripts/smoke_test.py
```

结果：**289/289 项断言通过**。覆盖：

- 公开检索的 6 类筛选/排序/分页边界、全文检索、详情、流派；
- 注册（用户名/邮箱/格式/重复）、登录（种子账号/错误密码/停用）、me、登出；
- 收藏防重/取消、评分 created/updated/取消、评论发表/修改/越权/管理员删除；
- 诗人/流派/诗集/诗歌的新增、修改、删除、下架恢复；
- 删除有作品诗人被触发器拦截、删除有互动诗歌被外键拦截、无效诗歌 ID 创建诗集整体回滚；
- CORS 预检、未知来源拒绝、`JSESSIONID` Cookie。

## 6. 已知差异

正常业务路径与原 Java 版一致；以下边界行为有意做了更可读的处理：

1. 缺少必填查询参数或 JSON 格式错误返回 `code=400`，原 Java 版兜底为 `code=500`；
2. 注销采用删除签名 Cookie，浏览器端立即失效；服务端不再保存会话记录（原 Java HttpSession 会在服务端失效）；
3. 不创建 `django_session` 等框架表，数据库结构仍是课程设计的 10 张表。

## 7. 后续可选工作

- 若需要严格的服务端会话失效，可切换到 Django 数据库会话（会新增 `django_session` 表）；
- 若后续补前端，可直接沿用现有 API，无需改动字段或 Cookie 方案；
- Java 版已移除；当前仓库只保留 Django 版本，原实现可在 git 历史中查看。
