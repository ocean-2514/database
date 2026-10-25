-- 03_indexes.sql - 中文全文索引
-- MySQL 8.0.16+ 的 InnoDB ngram parser 用于中文标题和正文检索。
-- 普通 B+Tree 索引及唯一索引已在 02_create_tables.sql 中定义。
USE poetry_db;
SET NAMES utf8mb4;

ALTER TABLE poem
  ADD FULLTEXT INDEX ft_poem_title (title) WITH PARSER ngram,
  ADD FULLTEXT INDEX ft_poem_content (content) WITH PARSER ngram;