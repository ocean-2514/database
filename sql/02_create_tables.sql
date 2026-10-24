-- =============================================================
-- 02_create_tables.sql —— 基本表定义
-- 《诗歌信息检索与赏析管理系统》数据库脚本 2/7
-- 8 个实体表 + 2 个 m:n 联系表 = 10 张表
-- 命名约定: fk_ 外键约束 / uk_ 唯一约束 / chk_ 检查约束 / idx_ 普通索引
-- 说明:
--   * 表名 `user`、`comment` 与关键字同名, 统一加反引号;
--   * 评分记录 / 收藏记录是联系实体, 以 UNIQUE(user_id, poem_id)
--     保证同一用户对同一首诗只有一条评分 / 收藏;
--   * poem.word_count 为反范式冗余列, 由 05 脚本中的触发器维护;
--   * 删除策略: 互动数据(评分/评论/收藏)随用户或诗歌级联删除;
--     诗人被诗歌引用时禁止删除(RESTRICT + 触发器给出友好提示)。
-- =============================================================
USE poetry_db;
SET NAMES utf8mb4;

-- 1. 诗人
CREATE TABLE poet (
    poet_id     BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '诗人ID',
    name        VARCHAR(50)       NOT NULL COMMENT '姓名',
    pen_name    VARCHAR(50)       NULL COMMENT '笔名',
    gender      ENUM('男','女')   NOT NULL DEFAULT '男' COMMENT '性别',
    birth_year  SMALLINT UNSIGNED NULL COMMENT '生年',
    death_year  SMALLINT UNSIGNED NULL COMMENT '卒年(在世诗人为NULL)',
    nationality VARCHAR(30)       NOT NULL DEFAULT '中国' COMMENT '国籍',
    biography   TEXT              NULL COMMENT '简介',
    PRIMARY KEY (poet_id),
    KEY idx_poet_name_year (name, birth_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='诗人表';

-- 2. 诗歌(核心实体)
CREATE TABLE poem (
    poem_id      BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '诗歌ID',
    title        VARCHAR(100)      NOT NULL COMMENT '标题',
    content      MEDIUMTEXT        NOT NULL COMMENT '正文',
    create_year  SMALLINT UNSIGNED NULL COMMENT '创作年份',
    form         VARCHAR(20)       NULL COMMENT '体裁: 自由诗/散文诗/十四行诗等',
    word_count   INT UNSIGNED      NOT NULL DEFAULT 0 COMMENT '字数(触发器依据正文自动维护)',
    appreciation TEXT              NULL COMMENT '赏析',
    poet_id      BIGINT UNSIGNED   NOT NULL COMMENT '所属诗人',
    PRIMARY KEY (poem_id),
    KEY idx_poem_title (title),
    KEY idx_poem_year (create_year),
    CONSTRAINT fk_poem_poet FOREIGN KEY (poet_id) REFERENCES poet (poet_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='诗歌表';

-- 3. 诗集
CREATE TABLE collection (
    collection_id BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '诗集ID',
    title         VARCHAR(100)      NOT NULL COMMENT '诗集名称',
    publish_year  SMALLINT UNSIGNED NULL COMMENT '出版年份',
    publisher     VARCHAR(100)      NULL COMMENT '出版社',
    isbn          VARCHAR(20)       NULL COMMENT 'ISBN',
    introduction  TEXT              NULL COMMENT '简介',
    PRIMARY KEY (collection_id),
    UNIQUE KEY uk_collection_isbn (isbn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='诗集表';

-- 4. 流派
CREATE TABLE genre (
    genre_id    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '流派ID',
    name        VARCHAR(50)     NOT NULL COMMENT '流派名称',
    description VARCHAR(500)    NULL COMMENT '描述',
    PRIMARY KEY (genre_id),
    UNIQUE KEY uk_genre_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流派表';

-- 5. 用户
CREATE TABLE `user` (
    user_id       BIGINT UNSIGNED         NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    username      VARCHAR(30)             NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255)            NOT NULL COMMENT '密码哈希(BCrypt等), 严禁明文',
    email         VARCHAR(100)            NULL COMMENT '邮箱',
    role          ENUM('reader','admin')  NOT NULL DEFAULT 'reader' COMMENT '角色: 读者/管理员',
    status        ENUM('active','banned') NOT NULL DEFAULT 'active' COMMENT '账户状态',
    register_time DATETIME                NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_user_username (username),
    UNIQUE KEY uk_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 6. 评分记录(联系实体)
CREATE TABLE rating (
    rating_id   BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT COMMENT '评分记录ID',
    user_id     BIGINT UNSIGNED  NOT NULL COMMENT '评分用户',
    poem_id     BIGINT UNSIGNED  NOT NULL COMMENT '被评诗歌',
    score       TINYINT UNSIGNED NOT NULL COMMENT '评分(1-5)',
    rating_time DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评分时间',
    PRIMARY KEY (rating_id),
    UNIQUE KEY uk_rating_user_poem (user_id, poem_id),
    CONSTRAINT chk_rating_score CHECK (score BETWEEN 1 AND 5),
    CONSTRAINT fk_rating_user FOREIGN KEY (user_id) REFERENCES `user` (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rating_poem FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评分记录表';

-- 7. 评论
CREATE TABLE `comment` (
    comment_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    user_id      BIGINT UNSIGNED NOT NULL COMMENT '评论用户',
    poem_id      BIGINT UNSIGNED NOT NULL COMMENT '被评诗歌',
    content      TEXT            NOT NULL COMMENT '评论内容',
    comment_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
    like_count   INT UNSIGNED    NOT NULL DEFAULT 0 COMMENT '点赞数',
    PRIMARY KEY (comment_id),
    KEY idx_comment_poem_time (poem_id, comment_time),
    CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES `user` (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_comment_poem FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评论表';

-- 8. 收藏记录(联系实体)
CREATE TABLE favorite (
    favorite_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '收藏记录ID',
    user_id       BIGINT UNSIGNED NOT NULL COMMENT '收藏用户',
    poem_id       BIGINT UNSIGNED NOT NULL COMMENT '被藏诗歌',
    favorite_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    favorite_type VARCHAR(20)     NOT NULL DEFAULT '默认' COMMENT '收藏类型: 默认/最爱/想读等',
    PRIMARY KEY (favorite_id),
    UNIQUE KEY uk_favorite_user_poem (user_id, poem_id),
    CONSTRAINT fk_favorite_user FOREIGN KEY (user_id) REFERENCES `user` (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_favorite_poem FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收藏记录表';

-- 9. 诗歌-流派 (m:n 联系)
CREATE TABLE poem_genre (
    poem_id  BIGINT UNSIGNED NOT NULL COMMENT '诗歌ID',
    genre_id BIGINT UNSIGNED NOT NULL COMMENT '流派ID',
    PRIMARY KEY (poem_id, genre_id),
    CONSTRAINT fk_pg_poem  FOREIGN KEY (poem_id)  REFERENCES poem (poem_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pg_genre FOREIGN KEY (genre_id) REFERENCES genre (genre_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='诗歌-流派联系表';

-- 10. 诗集-诗歌 (m:n 联系, 含联系属性: 篇目序号)
CREATE TABLE collection_poem (
    collection_id BIGINT UNSIGNED   NOT NULL COMMENT '诗集ID',
    poem_id       BIGINT UNSIGNED   NOT NULL COMMENT '诗歌ID',
    seq_no        SMALLINT UNSIGNED NULL COMMENT '篇目序号',
    PRIMARY KEY (collection_id, poem_id),
    CONSTRAINT fk_cp_coll FOREIGN KEY (collection_id) REFERENCES collection (collection_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cp_poem FOREIGN KEY (poem_id)       REFERENCES poem (poem_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='诗集-诗歌联系表';
