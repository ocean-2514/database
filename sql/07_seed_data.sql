-- =============================================================
-- 07_seed_data.sql —— 种子数据
-- 《诗歌信息检索与赏析管理系统》数据库脚本 7/7
-- 说明:
--   * 数据仅用于课程演示, 诗歌正文均为节选;
--   * ISBN 为演示用虚构数据;
--   * password_hash 为真实 BCrypt 哈希, 演示密码: admin→admin123, reader1/reader2→reader123;
--     同一明文两次哈希结果不同(随机盐), 校验由后端 BCryptPasswordEncoder.matches 完成;
--   * word_count 无需手填, 由触发器 trg_poem_word_count_bi 维护。
-- =============================================================
USE poetry_db;
SET NAMES utf8mb4;

-- ---------- 流派 ----------
INSERT INTO genre (name, description) VALUES
('新月派',   '1923年前后兴起，提倡"三美"(音乐美、绘画美、建筑美)，代表诗人有徐志摩、闻一多等。'),
('现代派',   '20世纪30年代形成，以戴望舒、卞之琳为代表，追求朦胧的意象与现代情绪。'),
('朦胧诗派', '20世纪70年代末兴起，以北岛、舒婷、顾城为代表，强调个性表达与意象多义。'),
('第三代',   '20世纪80年代中期登上诗坛，主张口语化写作与日常经验，海子等亦活跃于此期。');

-- ---------- 诗人 ----------
INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography) VALUES
('徐志摩', '云中鹤', '男', 1897, 1931, '中国',
 '现代诗人、散文家，新月派代表人物，代表诗集《志摩的诗》《翡冷翠的一夜》。'),
('戴望舒', NULL, '男', 1905, 1950, '中国',
 '现代派象征主义诗人，因《雨巷》被称为"雨巷诗人"。'),
('海子', '查海生', '男', 1964, 1989, '中国',
 '当代诗人，代表作《面朝大海，春暖花开》《亚洲铜》，被视为朦胧诗后中国诗歌的重要标志。'),
('北岛', NULL, '男', 1949, NULL, '中国',
 '朦胧诗派代表诗人之一，代表作《回答》《一切》，曾主编《今天》杂志。'),
('舒婷', NULL, '女', 1952, NULL, '中国',
 '朦胧诗派代表诗人，代表作《致橡树》《祖国啊，我亲爱的祖国》。');

-- ---------- 诗歌 ----------
INSERT INTO poem (title, content, create_year, form, appreciation, poet_id) VALUES
('再别康桥',
 '轻轻的我走了，\n正如我轻轻的来；\n我轻轻的招手，\n作别西天的云彩。\n\n那河畔的金柳，\n是夕阳中的新娘；\n波光里的艳影，\n在我的心头荡漾。',
 1928, '自由诗',
 '以"轻轻的"复沓起笔，把离别的怅惘化为柔和的节奏与画面，是新月派"三美"主张的代表作。',
 (SELECT poet_id FROM poet WHERE name = '徐志摩')),
('偶然',
 '我是天空里的一片云，\n偶尔投影在你的波心——\n你不必讶异，\n更无须欢喜——\n在转瞬间消灭了踪影。',
 1926, '自由诗',
 '把偶然的相遇写得洒脱而克制，音韵圆融，是新月派格律化的典范之作。',
 (SELECT poet_id FROM poet WHERE name = '徐志摩')),
('雨巷',
 '撑着油纸伞，独自\n彷徨在悠长、悠长\n又寂寥的雨巷，\n我希望逢着\n一个丁香一样地\n结着愁怨的姑娘。',
 1927, '自由诗',
 '以"丁香"意象与回环的韵律营造朦胧忧愁的意境，象征主义手法与现代汉语的音色相得益彰。',
 (SELECT poet_id FROM poet WHERE name = '戴望舒')),
('面朝大海，春暖花开',
 '从明天起，做一个幸福的人\n喂马，劈柴，周游世界\n从明天起，关心粮食和蔬菜\n我有一所房子，面朝大海，春暖花开',
 1989, '自由诗',
 '明快的祝福语调之下藏着独属于诗人的孤独，温暖的日常意象构成当代诗歌中流传最广的篇章之一。',
 (SELECT poet_id FROM poet WHERE name = '海子')),
('回答',
 '卑鄙是卑鄙者的通行证，\n高尚是高尚者的墓志铭。',
 1976, '自由诗',
 '开篇两行以悖论式对仗概括一个时代的荒诞，是朦胧诗最具宣言色彩的名句。',
 (SELECT poet_id FROM poet WHERE name = '北岛')),
('致橡树',
 '我如果爱你——\n绝不像攀援的凌霄花，\n借你的高枝炫耀自己；\n我如果爱你——\n绝不学痴情的鸟儿，\n为绿荫重复单调的歌曲',
 1977, '自由诗',
 '以木棉与橡树的意象宣告独立平等的爱情观，是新时期女性意识觉醒的诗歌宣言。',
 (SELECT poet_id FROM poet WHERE name = '舒婷'));

-- ---------- 诗歌-流派 ----------
INSERT INTO poem_genre (poem_id, genre_id)
SELECT p.poem_id, g.genre_id
FROM poem p JOIN genre g
WHERE (p.title, g.name) IN
      (('再别康桥', '新月派'), ('偶然', '新月派'), ('雨巷', '现代派'),
       ('回答', '朦胧诗派'), ('致橡树', '朦胧诗派'), ('面朝大海，春暖花开', '第三代'));

-- ---------- 诗集 ----------
INSERT INTO collection (title, publish_year, publisher, isbn, introduction) VALUES
('新月诗选',   1931, '新月书店',         '978-7-000-00001-1', '陈梦家编选的新月派诗人合集，收录徐志摩、闻一多等十八家作品。'),
('朦胧诗选',   1985, '春风文艺出版社',   '978-7-5313-00002-2', '国内最早的朦胧诗选本之一，收录北岛、舒婷、顾城等诗人作品。'),
('海子的诗',   1995, '人民文学出版社',   '978-7-02-000003-3', '海子诗歌精选集，收录其抒情短诗与长诗节选。');

-- ---------- 诗集-诗歌 ----------
INSERT INTO collection_poem (collection_id, poem_id, seq_no)
SELECT c.collection_id, p.poem_id, t.seq
FROM (SELECT '新月诗选' AS ctitle, '再别康桥' AS ptitle, 1 AS seq
      UNION SELECT '新月诗选', '偶然', 2
      UNION SELECT '朦胧诗选', '回答', 1
      UNION SELECT '朦胧诗选', '致橡树', 2
      UNION SELECT '海子的诗', '面朝大海，春暖花开', 1) t
JOIN collection c ON c.title = t.ctitle
JOIN poem p       ON p.title = t.ptitle;

-- ---------- 用户 ----------
-- 密码(明文仅供课程演示): admin→admin123, reader1→reader123, reader2→reader123
INSERT INTO `user` (username, password_hash, email, role, status) VALUES
('admin',   '$2a$10$elqgHse9g5MVBk7p817WceePn/O3kQ.sgbmDbXpO5lLXUmU8YiQ/6', 'admin@poetry.cn',   'admin',  'active'),
('reader1', '$2a$10$Y7xaT/jCwdr8z1fmam..quXw0ROXtf0XwGYjoBHIcLaIIO4rPUygu', 'reader1@poetry.cn', 'reader', 'active'),
('reader2', '$2a$10$COITpZwDz7Vdy4b7dHtLxeddmxaQ6/5imY1vugrVilaEkiaSTnYzm', 'reader2@poetry.cn', 'reader', 'active');

-- ---------- 评分 ----------
INSERT INTO rating (user_id, poem_id, score) VALUES
((SELECT user_id FROM `user` WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '再别康桥'), 5),
((SELECT user_id FROM `user` WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'), 5),
((SELECT user_id FROM `user` WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'), 4),
((SELECT user_id FROM `user` WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '回答'), 5),
((SELECT user_id FROM `user` WHERE username = 'admin'),   (SELECT poem_id FROM poem WHERE title = '雨巷'), 4);

-- ---------- 评论 ----------
INSERT INTO `comment` (user_id, poem_id, content, like_count) VALUES
((SELECT user_id FROM `user` WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '再别康桥'),
 '每读一遍都有新的感受，音韵太美了。', 12),
((SELECT user_id FROM `user` WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'),
 '明亮的句子背后藏着孤独，越读越动人。', 8),
((SELECT user_id FROM `user` WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '回答'),
 '开篇即是宣言，震撼。', 15);

-- ---------- 收藏 ----------
INSERT INTO favorite (user_id, poem_id, favorite_type) VALUES
((SELECT user_id FROM `user` WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '面朝大海，春暖花开'), '最爱'),
((SELECT user_id FROM `user` WHERE username = 'reader1'), (SELECT poem_id FROM poem WHERE title = '雨巷'), '默认'),
((SELECT user_id FROM `user` WHERE username = 'reader2'), (SELECT poem_id FROM poem WHERE title = '再别康桥'), '默认');

-- =============================================================
-- 验证(可选):
--   SELECT * FROM v_poem_brief;
--   SELECT * FROM v_poem_detail WHERE title = '再别康桥'\G
--   SELECT * FROM v_collection_catalog;
--   SELECT title, word_count FROM poem;   -- 字数应已被触发器填好
-- =============================================================
