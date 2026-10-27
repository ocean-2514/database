-- 06_procedures.sql - 检索、注册与事务式诗集收录
USE poetry_db;
SET NAMES utf8mb4;

DELIMITER $$

-- 可空筛选项表示忽略；p_order_by: 0=最新, 1=平均分, 2=标题。
-- 返回总数和当前页两个结果集。
CREATE PROCEDURE sp_search_poems (
  IN p_keyword VARCHAR(255),
  IN p_poet_name VARCHAR(100),
  IN p_genre_name VARCHAR(100),
  IN p_year_from SMALLINT,
  IN p_year_to SMALLINT,
  IN p_collection_name VARCHAR(200),
  IN p_order_by TINYINT,
  IN p_page INT,
  IN p_page_size INT
)
BEGIN
  DECLARE v_page INT;
  DECLARE v_page_size INT;
  DECLARE v_offset INT;

  SET v_page = GREATEST(COALESCE(p_page, 1), 1);
  SET v_page_size = LEAST(GREATEST(COALESCE(p_page_size, 10), 1), 100);
  SET v_offset = (v_page - 1) * v_page_size;

  SELECT COUNT(DISTINCT p.poem_id) AS total_count
  FROM poem AS p
  JOIN poet AS pt ON pt.poet_id = p.poet_id
  WHERE p.publication_status = 'published'
    AND (p_keyword IS NULL OR p.title LIKE CONCAT('%', p_keyword, '%')
         OR p.content LIKE CONCAT('%', p_keyword, '%'))
    AND (p_poet_name IS NULL OR pt.name LIKE CONCAT('%', p_poet_name, '%'))
    AND (p_year_from IS NULL OR p.creation_year >= p_year_from)
    AND (p_year_to IS NULL OR p.creation_year <= p_year_to)
    AND (p_genre_name IS NULL OR EXISTS (
      SELECT 1
      FROM poem_genre AS pg
      JOIN genre AS g ON g.genre_id = pg.genre_id
      WHERE pg.poem_id = p.poem_id
        AND g.genre_name LIKE CONCAT('%', p_genre_name, '%')
    ))
    AND (p_collection_name IS NULL OR EXISTS (
      SELECT 1
      FROM collection_poem AS cp
      JOIN poetry_collection AS pc ON pc.collection_id = cp.collection_id
      WHERE cp.poem_id = p.poem_id
        AND pc.collection_name LIKE CONCAT('%', p_collection_name, '%')
    ));

  SELECT p.poem_id,
         p.title,
         pt.name AS poet_name,
         p.creation_year,
         p.poem_form,
         CHAR_LENGTH(p.content) AS word_count,
         COALESCE(r.avg_score, 0) AS avg_score,
         COALESCE(r.rating_count, 0) AS rating_count
  FROM poem AS p
  JOIN poet AS pt ON pt.poet_id = p.poet_id
  LEFT JOIN (
    SELECT poem_id, AVG(score) AS avg_score, COUNT(*) AS rating_count
    FROM poem_rating
    GROUP BY poem_id
  ) AS r ON r.poem_id = p.poem_id
  WHERE p.publication_status = 'published'
    AND (p_keyword IS NULL OR p.title LIKE CONCAT('%', p_keyword, '%')
         OR p.content LIKE CONCAT('%', p_keyword, '%'))
    AND (p_poet_name IS NULL OR pt.name LIKE CONCAT('%', p_poet_name, '%'))
    AND (p_year_from IS NULL OR p.creation_year >= p_year_from)
    AND (p_year_to IS NULL OR p.creation_year <= p_year_to)
    AND (p_genre_name IS NULL OR EXISTS (
      SELECT 1
      FROM poem_genre AS pg
      JOIN genre AS g ON g.genre_id = pg.genre_id
      WHERE pg.poem_id = p.poem_id
        AND g.genre_name LIKE CONCAT('%', p_genre_name, '%')
    ))
    AND (p_collection_name IS NULL OR EXISTS (
      SELECT 1
      FROM collection_poem AS cp
      JOIN poetry_collection AS pc ON pc.collection_id = cp.collection_id
      WHERE cp.poem_id = p.poem_id
        AND pc.collection_name LIKE CONCAT('%', p_collection_name, '%')
    ))
  ORDER BY
    CASE WHEN p_order_by = 1 THEN r.avg_score END DESC,
    CASE WHEN p_order_by = 2 THEN p.title END ASC,
    p.created_at DESC,
    p.poem_id DESC
  LIMIT v_page_size OFFSET v_offset;
END$$

-- 中文全文检索；单字短词由调用方按设计说明使用 LIKE 兜底。
CREATE PROCEDURE sp_fulltext_search_poems(IN p_keyword VARCHAR(255))
BEGIN
  SELECT p.poem_id,
         p.title,
         pt.name AS poet_name,
         p.creation_year AS create_year,
         MATCH(p.title) AGAINST (p_keyword IN NATURAL LANGUAGE MODE)
           + MATCH(p.content) AGAINST (p_keyword IN NATURAL LANGUAGE MODE) AS relevance
  FROM poem AS p
  JOIN poet AS pt ON pt.poet_id = p.poet_id
  WHERE p.publication_status = 'published'
    AND (MATCH(p.title) AGAINST (p_keyword IN NATURAL LANGUAGE MODE) > 0
         OR MATCH(p.content) AGAINST (p_keyword IN NATURAL LANGUAGE MODE) > 0)
  ORDER BY relevance DESC, p.poem_id DESC;
END$$

-- 注册不接受角色参数；新用户始终使用默认普通用户角色。
CREATE PROCEDURE sp_register_user(
  IN p_username VARCHAR(50),
  IN p_password_hash VARCHAR(255),
  IN p_email VARCHAR(254),
  OUT p_user_id BIGINT UNSIGNED
)
BEGIN
  IF EXISTS (SELECT 1 FROM app_user WHERE username = p_username)
     OR EXISTS (SELECT 1 FROM app_user WHERE email = p_email) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '用户名或邮箱已存在';
  END IF;

  INSERT INTO app_user (username, password_hash, email)
  VALUES (p_username, p_password_hash, p_email);
  SET p_user_id = LAST_INSERT_ID();
END$$

-- 新建诗集并按输入顺序收录诗歌；任一 ID 无效时整个操作回滚。
-- p_poem_ids 示例: '12,18,25'，列表位置成为 sequence_no。
CREATE PROCEDURE sp_add_collection_with_poems(
  IN p_collection_name VARCHAR(200),
  IN p_publication_year SMALLINT UNSIGNED,
  IN p_publisher VARCHAR(200),
  IN p_isbn VARCHAR(20),
  IN p_description TEXT,
  IN p_poem_ids VARCHAR(2000)
)
BEGIN
  DECLARE v_collection_id BIGINT UNSIGNED;
  DECLARE v_rest VARCHAR(2000);
  DECLARE v_item VARCHAR(20);
  DECLARE v_sequence_no INT UNSIGNED DEFAULT 0;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;
  INSERT INTO poetry_collection
    (collection_name, publication_year, publisher, isbn, description)
  VALUES
    (p_collection_name, p_publication_year, p_publisher, p_isbn, p_description);
  SET v_collection_id = LAST_INSERT_ID();
  SET v_rest = TRIM(COALESCE(p_poem_ids, ''));

  WHILE v_rest <> '' DO
    SET v_item = TRIM(SUBSTRING_INDEX(v_rest, ',', 1));
    SET v_sequence_no = v_sequence_no + 1;
    INSERT INTO collection_poem (collection_id, poem_id, sequence_no)
    VALUES (v_collection_id, CAST(v_item AS UNSIGNED), v_sequence_no);

    IF LOCATE(',', v_rest) > 0 THEN
      SET v_rest = SUBSTRING(v_rest, LOCATE(',', v_rest) + 1);
    ELSE
      SET v_rest = '';
    END IF;
  END WHILE;

  COMMIT;
END$$

DELIMITER ;