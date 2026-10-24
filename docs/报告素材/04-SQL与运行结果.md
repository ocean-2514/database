# 04 SQL 与运行结果素材

> 本文提供 SQL 结构和检查语句模板。当前文件不包含数据库执行记录或实测结果；运行结果、截图和执行环境信息应由小组连接目标 MySQL 后填写。SQL 文件以 `db/sql/` 为准。

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
| `sp_search_poems` | 按关键词、诗人、朝代、年份、流派和诗集筛选并分页 |
| `sp_fulltext_search_poems` | 标题与正文 ngram 全文检索 |
| `sp_register_user` | 以普通用户默认角色注册 |
| `sp_add_collection_with_poems` | 事务式创建诗集并按顺序收录诗歌 |

触发器不维护派生字数。其职责包括阻止删除仍有诗歌的诗人、阻止物理删除管理员账户，以及校验评分时间不能晚于当前时间。

## 3. 执行后可记录的查询

```sql
-- 已发布诗歌及派生字数
SELECT poem_id, title, poet_name, creation_year, word_count
FROM v_poem_brief
ORDER BY creation_year, poem_id;

-- 组合检索过程示例：忽略筛选条件，按最新排序，第一页 10 条
CALL sp_search_poems(NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 1, 10);

-- 分类查看数据库对象
SHOW FULL TABLES;
SHOW INDEX FROM poem;
```

执行后请在报告中补录日期、MySQL 版本、实际行数、关键输出截图，以及约束拒绝无效数据的实际结果。不要将预期结果写成已经执行的事实。