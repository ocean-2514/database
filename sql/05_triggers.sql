-- 05_triggers.sql - 数据库端业务保护
-- 派生字数不落表，因此不需要字数维护触发器。
USE poetry_db;
SET NAMES utf8mb4;

DELIMITER $$

CREATE TRIGGER trg_poet_bd
BEFORE DELETE ON poet
FOR EACH ROW
BEGIN
  IF EXISTS (SELECT 1 FROM poem WHERE poet_id = OLD.poet_id) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '该诗人名下仍有诗歌，不能删除';
  END IF;
END$$

CREATE TRIGGER trg_app_user_bd
BEFORE DELETE ON app_user
FOR EACH ROW
BEGIN
  IF OLD.role = 'admin' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '管理员账户不能物理删除，请先停用账户';
  END IF;
END$$

CREATE TRIGGER trg_rating_bi
BEFORE INSERT ON poem_rating
FOR EACH ROW
BEGIN
  IF NEW.rated_at > CURRENT_TIMESTAMP THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '评分时间不能晚于当前时间';
  END IF;
END$$

CREATE TRIGGER trg_rating_bu
BEFORE UPDATE ON poem_rating
FOR EACH ROW
BEGIN
  IF NEW.rated_at > CURRENT_TIMESTAMP THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '评分时间不能晚于当前时间';
  END IF;
END$$

DELIMITER ;