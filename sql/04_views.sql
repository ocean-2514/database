-- 04_views.sql - 面向列表、详情与诗集目录的只读外模式
USE poetry_db;
SET NAMES utf8mb4;

-- 列表视图仅暴露已发布诗歌；字数及统计值在查询时派生。
CREATE OR REPLACE VIEW v_poem_brief AS
SELECT p.poem_id,
       p.title,
       pt.poet_id,
       pt.name AS poet_name,
       pt.dynasty,
       p.creation_year,
       p.poem_form,
       CHAR_LENGTH(p.content) AS word_count,
       COALESCE(r.avg_score, 0) AS avg_score,
       COALESCE(r.rating_count, 0) AS rating_count,
       COALESCE(c.comment_count, 0) AS comment_count,
       COALESCE(f.favorite_count, 0) AS favorite_count
FROM poem AS p
JOIN poet AS pt ON pt.poet_id = p.poet_id
LEFT JOIN (
  SELECT poem_id, ROUND(AVG(score), 2) AS avg_score, COUNT(*) AS rating_count
  FROM poem_rating
  GROUP BY poem_id
) AS r ON r.poem_id = p.poem_id
LEFT JOIN (
  SELECT poem_id, COUNT(*) AS comment_count
  FROM poem_comment
  GROUP BY poem_id
) AS c ON c.poem_id = p.poem_id
LEFT JOIN (
  SELECT poem_id, COUNT(*) AS favorite_count
  FROM poem_favorite
  GROUP BY poem_id
) AS f ON f.poem_id = p.poem_id
WHERE p.publication_status = 'published';

-- 诗歌详情视图；评论正文由独立分页查询读取。
CREATE OR REPLACE VIEW v_poem_detail AS
SELECT p.poem_id,
       p.title,
       p.content,
       p.creation_year,
       p.poem_form,
       p.appreciation,
       p.publication_status,
       p.created_at,
       p.updated_at,
       CHAR_LENGTH(p.content) AS word_count,
       pt.poet_id,
       pt.name AS poet_name,
       pt.pen_name,
       pt.gender,
       pt.birth_year,
       pt.death_year,
       pt.nationality,
       pt.dynasty,
       COALESCE(g.genres, '') AS genres,
       COALESCE(co.collections, '') AS collections,
       COALESCE(r.avg_score, 0) AS avg_score,
       COALESCE(r.rating_count, 0) AS rating_count,
       COALESCE(c.comment_count, 0) AS comment_count,
       COALESCE(f.favorite_count, 0) AS favorite_count
FROM poem AS p
JOIN poet AS pt ON pt.poet_id = p.poet_id
LEFT JOIN (
  SELECT pg.poem_id,
         GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR '、') AS genres
  FROM poem_genre AS pg
  JOIN genre AS g ON g.genre_id = pg.genre_id
  GROUP BY pg.poem_id
) AS g ON g.poem_id = p.poem_id
LEFT JOIN (
  SELECT cp.poem_id,
         GROUP_CONCAT(pc.collection_name ORDER BY cp.sequence_no SEPARATOR '、') AS collections
  FROM collection_poem AS cp
  JOIN poetry_collection AS pc ON pc.collection_id = cp.collection_id
  GROUP BY cp.poem_id
) AS co ON co.poem_id = p.poem_id
LEFT JOIN (
  SELECT poem_id, ROUND(AVG(score), 2) AS avg_score, COUNT(*) AS rating_count
  FROM poem_rating
  GROUP BY poem_id
) AS r ON r.poem_id = p.poem_id
LEFT JOIN (
  SELECT poem_id, COUNT(*) AS comment_count
  FROM poem_comment
  GROUP BY poem_id
) AS c ON c.poem_id = p.poem_id
LEFT JOIN (
  SELECT poem_id, COUNT(*) AS favorite_count
  FROM poem_favorite
  GROUP BY poem_id
) AS f ON f.poem_id = p.poem_id
WHERE p.publication_status = 'published';

-- 诗集目录；诗歌数量只统计已发布作品。
CREATE OR REPLACE VIEW v_collection_catalog AS
SELECT pc.collection_id,
       pc.collection_name,
       pc.publication_year,
       pc.publisher,
       pc.isbn,
       pc.description,
       COUNT(p.poem_id) AS poem_count
FROM poetry_collection AS pc
LEFT JOIN collection_poem AS cp ON cp.collection_id = pc.collection_id
LEFT JOIN poem AS p
  ON p.poem_id = cp.poem_id
 AND p.publication_status = 'published'
GROUP BY pc.collection_id, pc.collection_name, pc.publication_year,
         pc.publisher, pc.isbn, pc.description;