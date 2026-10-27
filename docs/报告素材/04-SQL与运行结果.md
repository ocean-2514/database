# 04 SQL 与运行结果素材

> 本文第 1—3 节提供 SQL 结构和检查语句模板，第 4 节为本组在 Django 后端与 MySQL 9.7.1 上的实测记录。运行结果、截图和执行环境信息应由小组连接目标 MySQL 后补充。SQL 文件以 `sql/` 为准。

## 1. 建库与表定义

新环境按顺序执行：`01_create_database.sql`、`02_create_tables.sql`、`03_indexes.sql`。也可用 `01_poetry_schema_mysql.sql` 一次创建数据库、表和全文索引。合并脚本与前三个脚本是两种互斥的初始化方式。

以下为核心表结构摘要，正式字段和约束以 `02_create_tables.sql` 为准：

```sql
CREATE TABLE poem (
  poem_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  content MEDIUMTEXT NOT NULL,
  creation_year SMALLINT NULL,
  poem_form VARCHAR(40) NULL,
  appreciation TEXT NULL,
  poet_id BIGINT UNSIGNED NOT NULL,
  publication_status ENUM('published', 'withdrawn') NOT NULL DEFAULT 'published',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (poem_id),
  KEY idx_poem_poet_year (poet_id, creation_year),
  KEY idx_poem_year (creation_year),
  CONSTRAINT fk_poem_poet FOREIGN KEY (poet_id) REFERENCES poet (poet_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (CHAR_LENGTH(TRIM(title)) > 0),
  CHECK (CHAR_LENGTH(TRIM(content)) > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

字数通过 `CHAR_LENGTH(content)` 查询计算，表中没有 `word_count` 列。互动表 `poem_rating` 与 `poem_favorite` 均对 `(user_id, poem_id)` 建唯一约束；评分另有 1—5 的 CHECK 约束。

## 2. 视图与数据库程序

| 对象 | 用途 |
|---|---|
| `v_poem_brief` | 已发布诗歌列表、派生字数和互动统计 |
| `v_poem_detail` | 已发布诗歌详情、作者、流派、诗集和互动统计 |
| `v_collection_catalog` | 诗集基本信息及已发布作品数量 |
| `sp_search_poems` | 按关键词、诗人、年份、流派和诗集筛选并分页 |
| `sp_fulltext_search_poems` | 标题与正文 ngram 全文检索 |
| `sp_register_user` | 以普通用户默认角色注册 |
| `sp_add_collection_with_poems` | 事务式创建诗集并按顺序收录诗歌 |

触发器不维护派生字数, 共 4 个: `trg_poet_bd` 阻止删除仍有诗歌的诗人; `trg_app_user_bd` 阻止物理删除管理员账户(应改为停用); `trg_rating_bi`/`trg_rating_bu` 在插入和更新评分时校验评分时间不得晚于当前时间。

## 3. 执行后可记录的查询

```sql
-- 已发布诗歌及派生字数
SELECT poem_id, title, poet_name, creation_year, word_count
FROM v_poem_brief
ORDER BY creation_year, poem_id;

-- 组合检索过程示例：忽略筛选条件，按最新排序，第一页 10 条
CALL sp_search_poems(NULL, NULL, NULL, NULL, NULL, NULL, 0, 1, 10);

-- 分类查看数据库对象
SHOW FULL TABLES;
SHOW INDEX FROM poem;
```

执行后请在报告中补录日期、MySQL 版本、实际行数、关键输出截图，以及约束拒绝无效数据的实际结果。不要将预期结果写成已经执行的事实。

## 4. 本组实测记录（2026-10-27，MySQL 9.7.1）

以下为 Django 后端按本设计完成适配后实际执行的接口与数据库结果。引用时请在报告中附截图。

| 场景 | 实测结果 |
|---|---|
| 初始化统计 | 诗人 18、诗歌 19、流派 5、用户 3、触发器 4、视图 3、FULLTEXT 索引 2 |
| 组合检索 `GET /api/poems?keyword=康桥` | total=1，返回《再别康桥》：createYear=1928，派生字数 68，平均分 5.0 |
| 全文检索 `keyword=春暖花开` | 命中《面朝大海，春暖花开》，相关度 9.81 |
| 派生字数 | 《再别康桥》68 字、《一代人》21 字（`CHAR_LENGTH(content)`，表中无 word_count 列） |
| 评分改分/取消 | 平均分联动 5.0 → 3.0 → 0.0（查询时聚合，无需维护统计列） |
| 注册缺邮箱 / 重复邮箱 | `400 邮箱不能为空` / `400 用户名或邮箱已存在` |
| 停用账户登录 | `400 账户已被停用` |
| 下架诗歌 `PUT /api/admin/poems/20/status?value=withdrawn` | 返回 200；公开详情报 `400 诗歌不存在或已下架`，检索不再命中，评分被拒；恢复 published 后一切正常 |
| 删除有作品的诗人 | `400 删除被数据库规则拦截: 该诗人名下仍有诗歌，不能删除`（触发器 trg_poet_bd） |
| 诗集收录无效诗歌 ID | `400 诗集创建失败(已整体回滚): foreign key constraint fails`，目录中无残留（事务回滚生效） |
| 物理删除无互动诗歌 | 返回 200；存在评分/评论/收藏时将被 RESTRICT 外键拦截，应改用下架 |
| 权限边界 | 未登录访问受保护接口 401；普通用户访问 `/api/admin/**` 403；评论改删非属主 403 |

Django 后端回归命令：`DB_NAME=poetry_db_test uv run python scripts/smoke_test.py`，当前 289/289 项断言通过（测试库 `poetry_db_test` 由 `scripts/init_test_db.sh` 从同一套 `sql/` 脚本初始化）。