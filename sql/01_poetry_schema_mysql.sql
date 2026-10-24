-- 诗歌信息检索与赏析管理系统
-- MySQL 8.0.16+ / InnoDB / utf8mb4
-- 核心实体共 8 个。poem_genre 与 collection_poem 为多对多联系表。

CREATE DATABASE IF NOT EXISTS poetry_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE poetry_db;

CREATE TABLE IF NOT EXISTS poet (
  poet_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  pen_name VARCHAR(100) NULL,
  gender VARCHAR(20) NULL,
  birth_year SMALLINT NULL COMMENT '负数表示公元前，NULL 表示未知',
  death_year SMALLINT NULL COMMENT '负数表示公元前，NULL 表示未知',
  nationality VARCHAR(64) NULL,
  dynasty VARCHAR(64) NULL,
  biography TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (poet_id),
  KEY idx_poet_name (name),
  KEY idx_poet_dynasty (dynasty, poet_id),
  CONSTRAINT chk_poet_life_years
    CHECK (birth_year IS NULL OR death_year IS NULL OR birth_year <= death_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='诗人';

CREATE TABLE IF NOT EXISTS poetry_collection (
  collection_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  collection_name VARCHAR(200) NOT NULL,
  publication_year SMALLINT UNSIGNED NULL,
  publisher VARCHAR(200) NULL,
  isbn VARCHAR(20) NULL,
  description TEXT NULL,
  PRIMARY KEY (collection_id),
  KEY idx_collection_name (collection_name),
  UNIQUE KEY uq_collection_isbn (isbn),
  CONSTRAINT chk_collection_publication_year
    CHECK (publication_year IS NULL OR publication_year BETWEEN 1000 AND 9999)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='诗集';

CREATE TABLE IF NOT EXISTS genre (
  genre_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  genre_name VARCHAR(100) NOT NULL,
  description TEXT NULL,
  PRIMARY KEY (genre_id),
  UNIQUE KEY uq_genre_name (genre_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='流派';

CREATE TABLE IF NOT EXISTS app_user (
  user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password_hash VARCHAR(255) NOT NULL COMMENT '只保存后端生成的密码哈希',
  email VARCHAR(254) NOT NULL,
  role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
  account_status ENUM('active', 'disabled') NOT NULL DEFAULT 'active',
  registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_app_user_username (username),
  UNIQUE KEY uq_app_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='系统用户';

CREATE TABLE IF NOT EXISTS poem (
  poem_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  content MEDIUMTEXT NOT NULL,
  creation_year SMALLINT NULL COMMENT '负数表示公元前，NULL 表示未知',
  poem_form VARCHAR(40) NULL,
  appreciation TEXT NULL,
  poet_id BIGINT UNSIGNED NOT NULL,
  publication_status ENUM('published', 'withdrawn') NOT NULL DEFAULT 'published',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (poem_id),
  KEY idx_poem_poet_year (poet_id, creation_year),
  KEY idx_poem_year (creation_year),
  FULLTEXT KEY ft_poem_title (title) WITH PARSER ngram,
  FULLTEXT KEY ft_poem_content (content) WITH PARSER ngram,
  CONSTRAINT fk_poem_poet
    FOREIGN KEY (poet_id) REFERENCES poet (poet_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_poem_title_nonempty CHECK (CHAR_LENGTH(TRIM(title)) > 0),
  CONSTRAINT chk_poem_content_nonempty CHECK (CHAR_LENGTH(content) > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='诗歌';

CREATE TABLE IF NOT EXISTS poem_genre (
  poem_id BIGINT UNSIGNED NOT NULL,
  genre_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (poem_id, genre_id),
  KEY idx_poem_genre_genre (genre_id, poem_id),
  CONSTRAINT fk_poem_genre_poem
    FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_poem_genre_genre
    FOREIGN KEY (genre_id) REFERENCES genre (genre_id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='诗歌-流派多对多联系';

CREATE TABLE IF NOT EXISTS collection_poem (
  collection_id BIGINT UNSIGNED NOT NULL,
  poem_id BIGINT UNSIGNED NOT NULL,
  sequence_no SMALLINT UNSIGNED NOT NULL COMMENT '诗集内顺序，从 1 开始',
  PRIMARY KEY (collection_id, poem_id),
  UNIQUE KEY uq_collection_sequence (collection_id, sequence_no),
  KEY idx_collection_poem_poem (poem_id, collection_id),
  CONSTRAINT fk_collection_poem_collection
    FOREIGN KEY (collection_id) REFERENCES poetry_collection (collection_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_collection_poem_poem
    FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT chk_collection_sequence_positive CHECK (sequence_no >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='诗集-诗歌多对多联系及编排顺序';

CREATE TABLE IF NOT EXISTS poem_rating (
  rating_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  poem_id BIGINT UNSIGNED NOT NULL,
  score TINYINT UNSIGNED NOT NULL,
  rated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (rating_id),
  UNIQUE KEY uq_rating_user_poem (user_id, poem_id),
  KEY idx_rating_poem_score (poem_id, score),
  CONSTRAINT fk_rating_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_rating_poem
    FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_rating_score CHECK (score BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='用户评分记录';

CREATE TABLE IF NOT EXISTS poem_comment (
  comment_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  poem_id BIGINT UNSIGNED NOT NULL,
  content TEXT NOT NULL,
  like_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '统计值；不记录逐用户点赞关系',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (comment_id),
  KEY idx_comment_poem_time (poem_id, created_at, comment_id),
  KEY idx_comment_user_time (user_id, created_at),
  CONSTRAINT fk_comment_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_comment_poem
    FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_comment_content_length
    CHECK (CHAR_LENGTH(TRIM(content)) BETWEEN 1 AND 2000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='诗歌评论';

CREATE TABLE IF NOT EXISTS poem_favorite (
  favorite_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  poem_id BIGINT UNSIGNED NOT NULL,
  favorited_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  favorite_type VARCHAR(50) NOT NULL DEFAULT '默认',
  PRIMARY KEY (favorite_id),
  UNIQUE KEY uq_favorite_user_poem (user_id, poem_id),
  KEY idx_favorite_poem (poem_id),
  CONSTRAINT fk_favorite_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_favorite_poem
    FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='用户收藏记录';

