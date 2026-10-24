-- =============================================================
-- 01_create_database.sql —— 创建数据库
-- 《诗歌信息检索与赏析管理系统》数据库脚本 1/7
-- 执行顺序: 01 → 02 → 03 → 04 → 05 → 06 → 07
-- 环境要求: MySQL 8.0.16 及以上
--   (8.0.16 起 CHECK 约束才强制生效; ngram 全文解析器需 5.7.6+)
-- 字符集: utf8mb4, 支持完整中文与生僻字
-- =============================================================

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS poetry_db;

CREATE DATABASE poetry_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE poetry_db;
