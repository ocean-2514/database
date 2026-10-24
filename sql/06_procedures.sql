-- =============================================================
-- 06_procedures.sql —— 存储过程与事务
-- 《诗歌信息检索与赏析管理系统》数据库脚本 6/7
-- 4 个存储过程: 组合检索 / 全文检索 / 用户注册 / 事务式建诗集
-- =============================================================
USE poetry_db;
SET NAMES utf8mb4;

DELIMITER $$

-- 1. 组合检索(分页): 组合条件全部可空, 传 NULL 即忽略该条件
--    p_order_by: 0 = 最新收录(poem_id 倒序)  1 = 平均分最高  2 = 标题升序
--    返回两个结果集: (1) 满足条件的总条数  (2) 当前页数据
CREATE PROCEDURE sp_search_poems (
    IN p_keyword   VARCHAR(100),
    IN p_poet_name VARCHAR(50),
    IN p_genre     VARCHAR(50),
    IN p_year_from SMALLINT UNSIGNED,
    IN p_year_to   SMALLINT UNSIGNED,
    IN p_order_by  TINYINT,
    IN p_page      INT,
    IN p_page_size INT
)
BEGIN
    DECLARE v_offset INT;
    SET v_offset = (p_page - 1) * p_page_size;

    SELECT COUNT(*) AS total_count
    FROM poem p
    JOIN poet pt ON pt.poet_id = p.poet_id
    WHERE (p_keyword   IS NULL OR p.title   LIKE CONCAT('%', p_keyword, '%')
                               OR p.content LIKE CONCAT('%', p_keyword, '%'))
      AND (p_poet_name IS NULL OR pt.name LIKE CONCAT('%', p_poet_name, '%'))
      AND (p_year_from IS NULL OR p.create_year >= p_year_from)
      AND (p_year_to   IS NULL OR p.create_year <= p_year_to)
      AND (p_genre     IS NULL OR p.poem_id IN (
             SELECT pg.poem_id
               FROM poem_genre pg
               JOIN genre g ON g.genre_id = pg.genre_id
              WHERE g.name LIKE CONCAT('%', p_genre, '%')));

    SELECT p.poem_id, p.title, pt.name AS poet_name, p.create_year, p.form,
           p.word_count,
           IFNULL((SELECT ROUND(AVG(r2.score), 1)
                     FROM rating r2 WHERE r2.poem_id = p.poem_id), 0) AS avg_score
    FROM poem p
    JOIN poet pt ON pt.poet_id = p.poet_id
    WHERE (p_keyword   IS NULL OR p.title   LIKE CONCAT('%', p_keyword, '%')
                               OR p.content LIKE CONCAT('%', p_keyword, '%'))
      AND (p_poet_name IS NULL OR pt.name LIKE CONCAT('%', p_poet_name, '%'))
      AND (p_year_from IS NULL OR p.create_year >= p_year_from)
      AND (p_year_to   IS NULL OR p.create_year <= p_year_to)
      AND (p_genre     IS NULL OR p.poem_id IN (
             SELECT pg.poem_id
               FROM poem_genre pg
               JOIN genre g ON g.genre_id = pg.genre_id
              WHERE g.name LIKE CONCAT('%', p_genre, '%')))
    ORDER BY
        CASE WHEN p_order_by = 1
             THEN IFNULL((SELECT AVG(r3.score) FROM rating r3
                           WHERE r3.poem_id = p.poem_id), 0) END DESC,
        CASE WHEN p_order_by = 2 THEN p.title END ASC,
        p.poem_id DESC
    LIMIT p_page_size OFFSET v_offset;
END$$

-- 2. 全文检索: MATCH...AGAINST + ngram 解析器(与 LIKE 模糊检索互补)
--    relevance 为相关度得分, 越大越相关
CREATE PROCEDURE sp_fulltext_search_poems (IN p_keyword VARCHAR(100))
BEGIN
    SELECT poem_id, title, create_year,
           MATCH(title, content) AGAINST (p_keyword IN NATURAL LANGUAGE MODE) AS relevance
    FROM poem
    WHERE MATCH(title, content) AGAINST (p_keyword IN NATURAL LANGUAGE MODE) > 0
    ORDER BY relevance DESC;
END$$

-- 3. 用户注册: 用户名查重后插入, OUT 参数返回新用户ID
CREATE PROCEDURE sp_register_user (
    IN  p_username      VARCHAR(30),
    IN  p_password_hash VARCHAR(255),
    IN  p_email         VARCHAR(100),
    OUT p_user_id       BIGINT UNSIGNED
)
BEGIN
    DECLARE v_cnt INT;
    SELECT COUNT(*) INTO v_cnt FROM `user` WHERE username = p_username;
    IF v_cnt > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '用户名已存在';
    ELSE
        INSERT INTO `user` (username, password_hash, email)
        VALUES (p_username, p_password_hash, p_email);
        SET p_user_id = LAST_INSERT_ID();
    END IF;
END$$

-- 4. 新建诗集并批量收录诗歌: 显式事务, 任一插入失败整体回滚
--    p_poem_ids 为逗号分隔的诗歌ID串, 如 '1,2,3'
CREATE PROCEDURE sp_add_collection_with_poems (
    IN p_title        VARCHAR(100),
    IN p_publish_year SMALLINT UNSIGNED,
    IN p_publisher    VARCHAR(100),
    IN p_isbn         VARCHAR(20),
    IN p_introduction TEXT,
    IN p_poem_ids     VARCHAR(1000)
)
BEGIN
    DECLARE v_coll_id BIGINT UNSIGNED;
    DECLARE v_rest    VARCHAR(1000);
    DECLARE v_item    VARCHAR(20);
    -- 出现任何 SQL 异常: 回滚事务并把原错误抛回调用方
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    INSERT INTO collection (title, publish_year, publisher, isbn, introduction)
    VALUES (p_title, p_publish_year, p_publisher, p_isbn, p_introduction);
    SET v_coll_id = LAST_INSERT_ID();

    SET v_rest = TRIM(BOTH ' ' FROM p_poem_ids);
    WHILE v_rest <> '' DO
        SET v_item = TRIM(BOTH ' ' FROM SUBSTRING_INDEX(v_rest, ',', 1));
        INSERT INTO collection_poem (collection_id, poem_id)
        VALUES (v_coll_id, CAST(v_item AS UNSIGNED));
        IF LOCATE(',', v_rest) > 0 THEN
            SET v_rest = SUBSTRING(v_rest, LOCATE(',', v_rest) + 1);
        ELSE
            SET v_rest = '';
        END IF;
    END WHILE;
    COMMIT;
END$$

DELIMITER ;

-- ---------------------------------------------------------------
-- 调用示例(执行完 07 种子数据后可运行验证):
--   CALL sp_search_poems('康桥', NULL, NULL, NULL, NULL, 2, 1, 10);
--   CALL sp_search_poems(NULL, NULL, '朦胧', 1970, 1990, 1, 1, 10);
--   CALL sp_fulltext_search_poems('春暖花开');
--   CALL sp_register_user('reader3', '$2a$10$abcdefg', 'r3@example.com', @uid);
--   SELECT @uid;
--   CALL sp_add_collection_with_poems('演示诗集', 2020, '演示出版社', NULL, '示例', '1,3,5');
-- ---------------------------------------------------------------
