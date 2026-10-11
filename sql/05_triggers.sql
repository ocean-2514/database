-- =============================================================
-- 05_triggers.sql —— 触发器
-- 《诗歌信息检索与赏析管理系统》数据库脚本 5/7
-- 5 个触发器: 2 个字数维护 + 3 个业务规则保护
-- =============================================================
USE poetry_db;
SET NAMES utf8mb4;

DELIMITER $$

-- 1. 插入诗歌时, 字数 = 正文字符数(含标点)
CREATE TRIGGER trg_poem_word_count_bi
BEFORE INSERT ON poem
FOR EACH ROW
BEGIN
    SET NEW.word_count = CHAR_LENGTH(NEW.content);
END$$

-- 2. 更新诗歌时, 正文有变化则重算字数 (<=> 为 NULL 安全等号)
CREATE TRIGGER trg_poem_word_count_bu
BEFORE UPDATE ON poem
FOR EACH ROW
BEGIN
    IF NOT (NEW.content <=> OLD.content) THEN
        SET NEW.word_count = CHAR_LENGTH(NEW.content);
    END IF;
END$$

-- 3. 删除诗人保护: 名下仍有诗歌则拒绝删除
--    (外键 RESTRICT 也会拦截, 触发器用于给出更友好的错误信息)
CREATE TRIGGER trg_poet_bd
BEFORE DELETE ON poet
FOR EACH ROW
BEGIN
    DECLARE v_cnt INT;
    SELECT COUNT(*) INTO v_cnt FROM poem WHERE poet_id = OLD.poet_id;
    IF v_cnt > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '该诗人名下仍有诗歌作品，禁止删除(请先处理其作品)';
    END IF;
END$$

-- 4. 管理员账户保护: 禁止删除管理员
CREATE TRIGGER trg_user_bd
BEFORE DELETE ON `user`
FOR EACH ROW
BEGIN
    IF OLD.role = 'admin' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '管理员账户禁止删除';
    END IF;
END$$

-- 5. 评分时间合法性: 不能晚于当前时间(防止脏数据)
CREATE TRIGGER trg_rating_bi
BEFORE INSERT ON rating
FOR EACH ROW
BEGIN
    IF NEW.rating_time > NOW() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '评分时间不能晚于当前时间';
    END IF;
END$$

DELIMITER ;
