-- =============================================================
-- 04_views.sql —— 视图(外模式/子模式)
-- 《诗歌信息检索与赏析管理系统》数据库脚本 4/7
-- 应用端优先面向视图查询, 屏蔽底层多表连接与聚合逻辑
-- =============================================================
USE poetry_db;
SET NAMES utf8mb4;

-- 1. 诗歌列表视图: 检索结果页 / 首页推荐直接查询
CREATE OR REPLACE VIEW v_poem_brief AS
SELECT p.poem_id,
       p.title,
       pt.name                AS poet_name,
       p.create_year,
       p.form,
       p.word_count,
       IFNULL(r.avg_score, 0)    AS avg_score,
       IFNULL(r.rating_cnt, 0)   AS rating_count,
       IFNULL(c.comment_cnt, 0)  AS comment_count,
       IFNULL(f.fav_cnt, 0)      AS favorite_count
FROM poem p
JOIN poet pt
    ON pt.poet_id = p.poet_id
LEFT JOIN (SELECT poem_id, ROUND(AVG(score), 1) AS avg_score, COUNT(*) AS rating_cnt
             FROM rating GROUP BY poem_id) r ON r.poem_id = p.poem_id
LEFT JOIN (SELECT poem_id, COUNT(*) AS comment_cnt
             FROM `comment` GROUP BY poem_id) c ON c.poem_id = p.poem_id
LEFT JOIN (SELECT poem_id, COUNT(*) AS fav_cnt
             FROM favorite GROUP BY poem_id) f ON f.poem_id = p.poem_id;

-- 2. 诗歌详情视图: 详情页一次查询取回诗歌 + 作者 + 流派 + 统计
CREATE OR REPLACE VIEW v_poem_detail AS
SELECT p.*,
       pt.name       AS poet_name,
       pt.pen_name,
       pt.birth_year,
       pt.death_year,
       (SELECT GROUP_CONCAT(g.name ORDER BY g.name SEPARATOR '、')
          FROM poem_genre pg
          JOIN genre g ON g.genre_id = pg.genre_id
         WHERE pg.poem_id = p.poem_id)                                   AS genres,
       IFNULL((SELECT ROUND(AVG(score), 1) FROM rating
               WHERE poem_id = p.poem_id), 0)                            AS avg_score,
       (SELECT COUNT(*) FROM `comment` WHERE poem_id = p.poem_id)        AS comment_count,
       (SELECT COUNT(*) FROM favorite  WHERE poem_id = p.poem_id)        AS favorite_count
FROM poem p
JOIN poet pt
    ON pt.poet_id = p.poet_id;

-- 3. 诗集目录视图: 诗集列表页
CREATE OR REPLACE VIEW v_collection_catalog AS
SELECT c.collection_id,
       c.title,
       c.publish_year,
       c.publisher,
       c.isbn,
       COUNT(cp.poem_id) AS poem_count
FROM collection c
LEFT JOIN collection_poem cp
    ON cp.collection_id = c.collection_id
GROUP BY c.collection_id, c.title, c.publish_year, c.publisher, c.isbn;
