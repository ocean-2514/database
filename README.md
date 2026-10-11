# 诗歌信息检索与赏析管理系统

《数据库系统原理》大作业 —— 面向现代诗歌的检索、赏析与互动系统。

| 成员 | 分工概要 |
| --- | --- |
| 钱湘智（组长） | 需求分析、功能设计、数据库设计（E-R 图 / 关系模式 / 3NF / 物理设计），辅助前后端 |
| 李梓源 | 系统架构、服务端概要设计、SQL 定义与操作（增删改查 / 触发器 / 存储过程 / 事务） |
| 石朋松 | Web 前端开发、Web 与数据库连接、SQL 调试 |

## 目录结构

```
database/
├── docs/
│   ├── 数据库大作业指导手册-应用系统设计与实现.md   # 课程要求原文
│   ├── 设计文档.md                                  # 题目提交说明(实体/联系/功能/分工)
│   └── er/
│       ├── 诗歌系统ER图.drawio                      # E-R 图源文件(3页:初步/诗歌域/用户域)
│       ├── gen_er_drawio.py                         # E-R 图生成脚本(python 运行)
│       └── ER图说明.md                              # 记法说明/Mermaid版/联系→关系模式映射
└── sql/
    ├── 01_create_database.sql                       # 建库(utf8mb4)
    ├── 02_create_tables.sql                         # 10 张表(8实体+2个m:n联系表)
    ├── 03_indexes.sql                               # 索引 + ngram 全文索引
    ├── 04_views.sql                                 # 视图(外模式): 列表/详情/诗集目录
    ├── 05_triggers.sql                              # 5 个触发器
    ├── 06_procedures.sql                            # 4 个存储过程(含事务)
    └── 07_seed_data.sql                             # 种子数据(现代诗歌节选)
```

## 环境要求

| 组件 | 版本 | 用途 |
| --- | --- | --- |
| MySQL | **8.0.16+**（必须） | 数据库；CHECK 约束自 8.0.16 起强制生效，全文检索依赖 ngram 解析器 |
| JDK | 17 或 21（本机已有 21） | Spring Boot 3 后端 |
| Maven | 3.9+（本机未装，可用 IDEA 内置） | 构建 |
| Node.js | 20 LTS（本机已有 24） | Vue 3 前端 |
| Python | 3.x（本机已有 3.13） | 重新生成 E-R 图源文件 |

## 数据库初始化

命令行（按序号执行，每个脚本内已 `USE poetry_db`）：

```bash
mysql -u root -p --default-character-set=utf8mb4 < sql/01_create_database.sql
mysql -u root -p --default-character-set=utf8mb4 < sql/02_create_tables.sql
mysql -u root -p --default-character-set=utf8mb4 < sql/03_indexes.sql
mysql -u root -p --default-character-set=utf8mb4 < sql/04_views.sql
mysql -u root -p --default-character-set=utf8mb4 < sql/05_triggers.sql
mysql -u root -p --default-character-set=utf8mb4 < sql/06_procedures.sql
mysql -u root -p --default-character-set=utf8mb4 < sql/07_seed_data.sql
```

或用 Workbench / DBeaver 依次打开执行。注意：

- 脚本内已含 `SET NAMES utf8mb4`，在 `mysql>` 提示符下用 `source D:/.../sql/xx.sql` 逐个加载也可以；
- **PowerShell 不支持 `<` 重定向**，请用 cmd 或 Git Bash；
- 中文 Windows 的命令行默认 GBK 编码，务必带 `--default-character-set=utf8mb4`，否则中文会乱码或建表失败。

完成后可用 `CALL sp_search_poems('康桥', NULL, NULL, NULL, NULL, 2, 1, 10);` 验证。

## 开发约定

- **所有数据库操作一律手写原生 SQL**（课程要求），后端用 MyBatis 时 SQL 写在 XML mapper 中，禁止使用 JPA/MyBatis-Generator 等 ORM 生成能力；
- 表名 `user`、`comment` 带反引号书写；
- 密码只存哈希（BCrypt 等），后端负责生成；
- Git：`main` 保持可运行版本，各人在自己的分支开发（如 `lzy`），合并前自测通过。

## 文档索引

- 设计类：`docs/设计文档.md`（题目与分工）、`docs/er/ER图说明.md`（E-R 图使用说明、联系→关系模式、3NF 判定要点）
- 指导手册要求的报告模板见 `docs/数据库大作业指导手册-应用系统设计与实现.md` 附录 1/2。
