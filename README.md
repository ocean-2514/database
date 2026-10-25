# 诗歌信息检索与赏析管理系统

《数据库系统原理》大作业。数据库设计以 `docs/子任务1-3_需求与数据库设计.md` 为准；本目录的表结构、SQL、E-R 图和报告素材均按该设计整理。

## 目录结构

```
db/
├── docs/
│   ├── 子任务1-3_需求与数据库设计.md     # 当前设计基准
│   ├── 设计文档.md                       # 选题与小组分工
│   ├── 数据库大作业指导手册-应用系统设计与实现.md
│   ├── er/                               # E-R 图源文件、生成脚本和说明
│   └── 报告素材/                         # 需求、架构、数据库设计、SQL素材
└── sql/
    ├── 01_create_database.sql
    ├── 02_create_tables.sql               # 8 个核心实体 + 2 个联系表
    ├── 03_indexes.sql                     # 中文 ngram 全文索引
    ├── 04_views.sql                       # 列表、详情、诗集目录视图
    ├── 05_triggers.sql                    # 删除保护、评分时间校验
    ├── 06_procedures.sql                  # 检索、注册、事务式诗集收录
    ├── 07_seed_data.sql
    ├── 08_expand_data.sql
    └── 01_poetry_schema_mysql.sql          # 01—03 的单文件建库/建表版本
```

## 设计约定

- MySQL 8.0.16+、InnoDB、`utf8mb4_0900_ai_ci`。
- 核心关系模式：`poet`、`poetry_collection`、`poem`、`genre`、`app_user`、`poem_rating`、`poem_comment`、`poem_favorite`、`poem_genre`、`collection_poem`。
- `poem.word_count` 不作为表字段保存；视图和检索结果用 `CHAR_LENGTH(content)` 派生。
- 诗歌通过 `publication_status` 下架；基础记录及互动记录的删除受外键限制，多对多联系随对应实体删除。
- 用户角色为 `user/admin`，账户状态为 `active/disabled`；管理员账户通过停用保留，不物理删除；密码字段仅保存哈希。
- 数据库排序规则使用户名和邮箱按不区分大小写方式比较；ISBN 写入前移除连字符，并将末位 `x` 统一为大写 `X`。
- `poem_comment.like_count` 是导入或统计值，不表示逐用户点赞关系。

## 初始化数据库

在 MySQL 客户端依次执行 `sql/01_create_database.sql` 至 `sql/08_expand_data.sql`。若只需创建数据库和结构，可执行 `01_create_database.sql`、`02_create_tables.sql`、`03_indexes.sql`；`01_poetry_schema_mysql.sql` 是这三步的合并版本，不要与前三个脚本重复执行。

也可通过 MySQL Workbench 或 DBeaver 按上述顺序运行。初始化脚本不会删除已有数据库；表和索引脚本主要用于新环境，重复创建全文索引前应确认索引尚不存在。

## 查询与演示

`04_views.sql` 创建 `v_poem_brief`、`v_poem_detail`、`v_collection_catalog`。`06_procedures.sql` 提供多条件检索、全文检索、普通用户注册和事务式诗集收录过程。演示数据脚本只用于课程样例；正文全文、人物年份和作品信息请按课程数据来源要求核对。

报告素材中提供的是设计说明和 SQL 参考。运行结果、截图和性能结论应在本组实际部署并执行后补充。

## 相关文档

- [子任务 1—3：需求与数据库设计](docs/子任务1-3_需求与数据库设计.md)
- [本次数据库设计对齐修改说明](docs/修改说明_数据库设计对齐.md)
- [报告素材索引](docs/报告素材/README.md)
