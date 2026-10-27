# 诗歌信息检索与赏析管理系统

《数据库系统原理》大作业。数据库设计以 `docs/子任务1-3_需求与数据库设计.md` 为准；表结构、SQL、E-R 图、后端与报告素材均按该设计整理。

| 成员 | 分工概要 |
| --- | --- |
| 钱湘智（组长） | 需求分析、功能设计、数据库设计（E-R 图 / 关系模式 / 3NF / 物理设计），辅助前后端 |
| 李梓源 | 系统架构、服务端概要设计、SQL 定义与操作（增删改查 / 触发器 / 存储过程 / 事务） |
| 石朋松 | Web 前端开发、Web 与数据库连接、SQL 调试 |

## 目录结构

```
database/
├── backend/                               # Spring Boot 3 服务器端
│   ├── pom.xml
│   ├── application-local.yml(.example)    # 本机数据库密码(真实文件不入库)
│   └── src/main/
│       ├── java/com/poetry/               # 入口、拦截器、控制器、服务、Mapper 接口、实体
│       └── resources/
│           ├── application.yml            # 数据源/MyBatis 配置
│           └── mapper/*.xml               # 全部 SQL 手写在这里(课程要求原生 SQL)
├── docs/
│   ├── 子任务1-3_需求与数据库设计.md      # 设计基准
│   ├── 设计文档.md                        # 选题与小组分工
│   ├── 数据库大作业指导手册-应用系统设计与实现.md
│   ├── er/                                # E-R 图源文件、生成脚本和说明
│   └── 报告素材/                          # 需求、架构、数据库设计、SQL 素材
└── sql/
    ├── 01_create_database.sql             # 建库(不删除已有库)
    ├── 02_create_tables.sql               # 8 个核心实体 + 2 个联系表
    ├── 03_indexes.sql                     # 标题/正文两个 ngram 全文索引
    ├── 04_views.sql                       # 列表、详情、诗集目录视图
    ├── 05_triggers.sql                    # 删除保护、评分时间校验(4 个触发器)
    ├── 06_procedures.sql                  # 检索、注册、事务式诗集收录(4 个存储过程)
    ├── 07_seed_data.sql
    ├── 08_expand_data.sql
    └── 01_poetry_schema_mysql.sql         # 01—03 的单文件合并版本
```

## 设计约定

- MySQL 8.0.16+、InnoDB、`utf8mb4_0900_ai_ci`。
- 核心关系模式：`poet`、`poetry_collection`、`poem`、`genre`、`app_user`、`poem_rating`、`poem_comment`、`poem_favorite`、`poem_genre`、`collection_poem`。
- `poem.word_count` 不作为表字段保存；视图和检索结果用 `CHAR_LENGTH(content)` 派生。
- 诗歌通过 `publication_status` 下架；基础记录及互动记录的删除受外键限制（RESTRICT），多对多联系随对应实体删除。
- 用户角色为 `user/admin`，账户状态为 `active/disabled`；管理员账户通过停用保留，不物理删除；密码字段仅保存哈希。
- 数据库排序规则使用户名和邮箱按不区分大小写方式比较；ISBN 写入前移除连字符，并将末位 `x` 统一为大写 `X`。
- `poem_comment.like_count` 是导入或统计值，不表示逐用户点赞关系。

## 初始化数据库

在 MySQL 客户端依次执行 `sql/01_create_database.sql` 至 `sql/08_expand_data.sql`。若只需创建数据库和结构，可执行 `01`、`02`、`03`；`01_poetry_schema_mysql.sql` 是这三步的合并版本，不要与前三个脚本重复执行。

```bash
mysql -u root -p --default-character-set=utf8mb4 < sql/01_create_database.sql
# ... 依次到 08
```

注意：

- 初始化脚本**不会删除已有数据库**；本地重建前需手动执行 `DROP DATABASE poetry_db;`；
- 中文 Windows 命令行默认 GBK，务必带 `--default-character-set=utf8mb4`；
- PowerShell 不支持 `<` 重定向，请用 cmd 或 Git Bash；
- 报告素材中提供的是设计说明和 SQL 参考；实测记录见 `docs/报告素材/04-SQL与运行结果.md` 第 4 节。

## 后端启动

```bash
cd backend
# 1) 配置数据库密码(二选一, 不要写进会提交的文件):
#    a) 复制 application-local.yml.example 为 application-local.yml, 填入你的密码(推荐)
#    b) 或设置环境变量 DB_PASSWORD
# 2) 启动(有 Maven 时):
mvn spring-boot:run
#    没有 Maven 时, 用 IDEA 打开 backend 目录直接运行 PoetryApplication
```

种子账户（执行 07 后生效）：`admin/admin123`（管理员）、`reader1/reader123`、`reader2/reader123`。

已实现 33 个接口（统一返回 `{code, message, data}`）：

| 接口 | 说明 | 数据库端 |
| --- | --- | --- |
| `GET /api/poems?keyword=&poetName=&genre=&yearFrom=&yearTo=&orderBy=&page=&pageSize=` | 组合检索(仅已发布), orderBy: 0最新 1评分最高 2标题 | poem JOIN poet + 动态条件(COUNT+LIMIT) |
| `GET /api/poems/fulltext?keyword=` | 中文全文检索(按相关度排序) | 存储过程 sp_fulltext_search_poems |
| `GET /api/poems/{id}` | 诗歌详情(派生字数/作者/流派/统计) | 视图 v_poem_detail |
| `GET /api/genres` | 流派列表 | genre 表 |
| `POST /api/auth/register` | 注册, JSON: `{username, password, email}`(邮箱必填) | 存储过程 sp_register_user(OUT 回填ID) |
| `POST /api/auth/login` | 登录, 成功后 Set-Cookie | BCrypt 校验 + app_user 表 |
| `GET /api/auth/me` | 当前登录用户(未登录 data=null) | Session |
| `POST /api/auth/logout` | 登出 | Session |
| `POST/DELETE /api/poems/{id}/favorite` | 收藏/取消(需登录) | poem_favorite, UNIQUE 防重 |
| `GET /api/favorites?page=&pageSize=` | 我的收藏(需登录, 只显示已发布作品) | poem_favorite JOIN poem/poet |
| `PUT /api/poems/{id}/rating?score=` | 评分/改分(需登录), data=created/updated | ON DUPLICATE KEY UPDATE 覆盖写, CHECK(1-5) |
| `GET /api/poems/{id}/rating` | 我的评分(需登录) | poem_rating |
| `DELETE /api/poems/{id}/rating` | 取消评分(需登录) | poem_rating |
| `GET /api/poems/{id}/comments?page=&pageSize=` | 评论列表(公开, 按时间倒序) | poem_comment JOIN app_user |
| `POST /api/poems/{id}/comments` | 发表评论(需登录), JSON: {content} | poem_comment, useGeneratedKeys |
| `PUT /api/comments/{id}` | 修改自己的评论(需登录) | 属主校验, 非属主 403 |
| `DELETE /api/comments/{id}` | 删除评论(需登录, 属主或管理员) | 属主/角色校验 |
| `GET/POST/PUT/DELETE /api/admin/poets` | 诗人管理(需管理员) | poet; 删除有作品者被触发器拦截 |
| `POST/PUT/DELETE /api/admin/poems` | 诗歌管理(需管理员); 物理删除受 RESTRICT 保护 | poem |
| `PUT /api/admin/poems/{id}/status?value=` | 下架/恢复(需管理员, published/withdrawn) | publication_status 状态变更 |
| `GET/POST/PUT/DELETE /api/admin/collections` | 诗集管理(需管理员), 新建调事务存储过程 | poetry_collection / sp_add_collection_with_poems |
| `POST/PUT/DELETE /api/admin/genres` | 流派管理(需管理员) | genre, UNIQUE 防重名 |

## 开发约定

- **所有数据库操作一律手写原生 SQL**（课程要求），MyBatis 仅做参数绑定与结果映射；
- 表名 `app_user` 等与关键字相近的标识符统一使用反引号或明确命名；
- 密码只存哈希（BCrypt），配置外置（密码不进 git）；
- Git：`main` 保持可运行版本，各人在自己的分支开发，合并前自测通过。

## 相关文档

- [子任务 1—3：需求与数据库设计](docs/子任务1-3_需求与数据库设计.md)
- [数据库设计对齐修改说明（含后续修订）](docs/修改说明_数据库设计对齐.md)
- [E-R 图说明](docs/er/ER图说明.md)
- [报告素材索引](docs/报告素材/README.md)
