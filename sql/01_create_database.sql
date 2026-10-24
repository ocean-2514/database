-- 01_create_database.sql - 创建数据库
-- MySQL 8.0.16+ / InnoDB / utf8mb4
-- 本脚本不删除已有数据库或数据。
CREATE DATABASE IF NOT EXISTS poetry_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE poetry_db;
SET NAMES utf8mb4;