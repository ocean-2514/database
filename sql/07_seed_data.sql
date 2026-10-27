-- 07_seed_data.sql - 课程演示用初始数据
-- 诗歌正文为节选；ISBN 为演示数据；账号密码只以 BCrypt 哈希保存。
-- poem.word_count 不落表，列表/详情查询用 CHAR_LENGTH(content) 派生。
USE poetry_db;
SET NAMES utf8mb4;

INSERT INTO genre (genre_name, description) VALUES
('新月派', '1923年前后兴起，提倡音乐美、绘画美、建筑美。'),
('现代派', '20世纪30年代形成，追求现代意象与情绪。'),
('朦胧诗派', '20世纪70年代末兴起，强调个性表达与意象多义。'),
('第三代', '20世纪80年代中期活跃，重视口语化写作与日常经验。');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography) VALUES
('徐志摩', '云中鹤', '男', 1897, 1931, '中国', '现代诗人、散文家，新月派代表人物。'),
('戴望舒', NULL, '男', 1905, 1950, '中国', '现代派象征主义诗人，因《雨巷》被称为“雨巷诗人”。'),
('海子', '查海生', '男', 1964, 1989, '中国', '当代诗人，代表作《面朝大海，春暖花开》《亚洲铜》。'),
('北岛', NULL, '男', 1949, NULL, '中国', '朦胧诗派代表诗人之一，代表作《回答》《一切》。'),
('舒婷', NULL, '女', 1952, NULL, '中国', '朦胧诗派代表诗人，代表作《致橡树》《祖国啊，我亲爱的祖国》。');

INSERT INTO poem (title, content, creation_year, poem_form, appreciation, poet_id) VALUES
('再别康桥',
 '轻轻的我走了，\n正如我轻轻的来；\n我轻轻的招手，\n作别西天的云彩。\n\n那河畔的金柳，\n是夕阳中的新娘；\n波光里的艳影，\n在我的心头荡漾。',
 1928, '自由诗', '以“轻轻的”复沓起笔，把离别的怅惘化为柔和的节奏与画面。',
 (SELECT poet_id FROM poet WHERE name = '徐志摩')),
('偶然',
 '我是天空里的一片云，\n偶尔投影在你的波心——\n你不必讶异，\n更无须欢喜——\n在转瞬间消灭了踪影。',
 1926, '自由诗', '把偶然的相遇写得洒脱而克制，音韵圆融。',
 (SELECT poet_id FROM poet WHERE name = '徐志摩')),
('雨巷',
 '撑着油纸伞，独自\n彷徨在悠长、悠长\n又寂寥的雨巷，\n我希望逢着\n一个丁香一样地\n结着愁怨的姑娘。',
 1927, '自由诗', '以丁香意象与回环韵律营造朦胧忧愁的意境。',
 (SELECT poet_id FROM poet WHERE name = '戴望舒')),
('面朝大海，春暖花开',
 '从明天起，做一个幸福的人\n喂马，劈柴，周游世界\n从明天起，关心粮食和蔬菜\n我有一所房子，面朝大海，春暖花开',
 1989, '自由诗', '明快的祝福语调之下藏着孤独，温暖的日常意象广为流传。',
 (SELECT poet_id FROM poet WHERE name = '海子')),
('回答',
 '卑鄙是卑鄙者的通行证，\n高尚是高尚者的墓志铭。',
 1976, '自由诗', '开篇两行以对仗概括一个时代的荒诞。',
 (SELECT poet_id FROM poet WHERE name = '北岛')),
('致橡树',
 '我如果爱你——\n绝不像攀援的凌霄花，\n借你的高枝炫耀自己；\n我如果爱你——\n绝不学痴情的鸟儿，\n为绿荫重复单调的歌曲',
 1977, '自由诗', '以木棉与橡树的意象表达独立平等的爱情观。',
 (SELECT poet_id FROM poet WHERE name = '舒婷'));

INSERT INTO poem_genre (poem_id, genre_id)
SELECT p.poem_id, g.genre_id
FROM poem AS p
JOIN genre AS g
WHERE (p.title, g.genre_name) IN
  (('再别康桥', '新月派'), ('偶然', '新月派'), ('雨巷', '现代派'),
   ('回答', '朦胧诗派'), ('致橡树', '朦胧诗派'), ('面朝大海，春暖花开', '第三代'));

INSERT INTO poetry_collection (collection_name, publication_year, publisher, isbn, description) VALUES
('新月诗选', 1931, '新月书店', '9787000000011', '课程演示用新月派诗歌合集。'),
('朦胧诗选', 1985, '春风文艺出版社', '9787531300002', '课程演示用朦胧诗选本。'),
('海子的诗', 1995, '人民文学出版社', '9787020000033', '课程演示用海子诗歌精选集。');

INSERT INTO collection_poem (collection_id, poem_id, sequence_no)
SELECT pc.collection_id, p.poem_id, t.sequence_no
FROM (
  SELECT '新月诗选' AS collection_name, '再别康桥' AS poem_title, 1 AS sequence_no
  UNION ALL SELECT '新月诗选', '偶然', 2
  UNION ALL SELECT '朦胧诗选', '回答', 1
  UNION ALL SELECT '朦胧诗选', '致橡树', 2
  UNION ALL SELECT '海子的诗', '面朝大海，春暖花开', 1
) AS t
JOIN poetry_collection AS pc ON pc.collection_name = t.collection_name
JOIN poem AS p ON p.title = t.poem_title;

-- 演示用户；仅用于本地课程环境，正式部署须更换哈希和邮箱。
INSERT INTO app_user (username, password_hash, email, role, account_status) VALUES
('admin', '$2a$10$elqgHse9g5MVBk7p817WceePn/O3kQ.sgbmDbXpO5lLXUmU8YiQ/6', 'admin@poetry.cn', 'admin', 'active'),
('reader1', '$2a$10$Y7xaT/jCwdr8z1fmam..quXw0ROXtf0XwGYjoBHIcLaIIO4rPUygu', 'reader1@poetry.cn', 'user', 'active'),
('reader2', '$2a$10$COITpZwDz7Vdy4b7dHtLxeddmxaQ6/5imY1vugrVilaEkiaSTnYzm', 'reader2@poetry.cn', 'user', 'active');

INSERT INTO poem_rating (user_id, poem_id, score) VALUES
((SELECT user_id FROM app_user WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '再别康桥'), 5),
((SELECT user_id FROM app_user WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'), 5),
((SELECT user_id FROM app_user WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'), 4),
((SELECT user_id FROM app_user WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '回答'), 5),
((SELECT user_id FROM app_user WHERE username = 'admin'), (SELECT poem_id FROM poem WHERE title = '雨巷'), 4);

INSERT INTO poem_comment (user_id, poem_id, content, like_count) VALUES
((SELECT user_id FROM app_user WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '再别康桥'), '每读一遍都有新的感受，音韵太美了。', 12),
((SELECT user_id FROM app_user WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'), '明亮的句子背后藏着孤独，越读越动人。', 8),
((SELECT user_id FROM app_user WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '回答'), '开篇即是宣言，震撼。', 15);

INSERT INTO poem_favorite (user_id, poem_id, favorite_type) VALUES
((SELECT user_id FROM app_user WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'), '最爱'),
((SELECT user_id FROM app_user WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '雨巷'), '默认'),
((SELECT user_id FROM app_user WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '再别康桥'), '默认');

-- 可选查询：SELECT * FROM v_poem_brief;
-- 派生字数：SELECT title, CHAR_LENGTH(content) AS word_count FROM poem;
