-- =============================================================
-- 03_indexes.sql —— 物理设计: 索引定义
-- 《诗歌信息检索与赏析管理系统》数据库脚本 3/7
-- 存取方法: B+树聚簇索引(主键) + 二级索引 + 全文索引
-- 说明:
--   * InnoDB 会为外键列自动创建索引, 02 脚本已建 title/create_year
--     等高频索引, 此处只补充检索加速与全文检索所需;
--   * ngram 解析器: 对中文按 2 字元滑窗切词, 使 MATCH...AGAINST
--     支持中文。查看/调整分词长度: @@ngram_token_size (默认 2, 需
--     在 my.ini 中配置后重启)。
-- =============================================================
USE poetry_db;
SET NAMES utf8mb4;

-- 中文全文索引(标题 + 正文), 支撑"按诗歌正文全文检索"功能
ALTER TABLE poem
    ADD FULLTEXT INDEX ft_poem_title_content (title, content) WITH PARSER ngram;

-- 按体裁筛选
ALTER TABLE poem
    ADD INDEX idx_poem_form (form);

-- 诗歌平均分聚合: 按 poem_id 汇总评分的高频操作
ALTER TABLE rating
    ADD INDEX idx_rating_poem_score (poem_id, score);
