-- =============================================================
-- 08_expand_data.sql —— 数据扩充: 近现代知名诗人与名篇
-- 《诗歌信息检索与赏析管理系统》数据库脚本 8/8
-- 在 07_seed_data.sql 之后执行, 可重复执行(幂等):
--   * 诗人/诗集按名称判重, 已存在则跳过;
--   * 诗歌按 (标题) 判重;
--   * 流派/诗集-诗歌 关系用 INSERT IGNORE(复合主键天然防重)。
-- 版权说明: 收录内容均为广为流传的短篇节选, 仅用于课程教学演示;
--   正式对外提供服务请使用公版作品或获得授权。
-- 说明: word_count 不手填, 由触发器 trg_poem_word_count_bi 自动维护;
--   新增流派"七月派"(艾青所属)。
-- =============================================================
USE poetry_db;
SET NAMES utf8mb4;

-- ---------- 新增流派 ----------
INSERT INTO genre (name, description)
SELECT '七月派', '20世纪30-40年代围绕《七月》等刊物形成的诗歌流派, 强调主观精神与现实的拥抱, 代表诗人有艾青、胡风等。'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM genre WHERE name = '七月派');

-- ---------- 新增诗人(13位, 一人一首名作) ----------
INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '闻一多', NULL, '男', 1899, 1946, '中国', '新月派代表诗人、学者, 提倡"三美", 代表诗集《红烛》《死水》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '闻一多');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '刘半农', NULL, '男', 1891, 1934, '中国', '新文化运动先驱, 语言学上首创"她"字, 代表作《教我如何不想她》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '刘半农');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '冰心', '谢婉莹', '女', 1900, 1999, '中国', '小诗体代表诗人、散文家, 出版诗集《繁星》《春水》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '冰心');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '林徽因', NULL, '女', 1904, 1955, '中国', '建筑学家、诗人, 代表作《你是人间的四月天》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '林徽因');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '卞之琳', NULL, '男', 1910, 2000, '中国', '现代派诗人, 诗风智性凝练, 代表作《断章》、诗集《鱼目集》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '卞之琳');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '郭沫若', NULL, '男', 1892, 1978, '中国', '新诗奠基人之一, 代表诗集《女神》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '郭沫若');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '艾青', NULL, '男', 1910, 1996, '中国', '七月派代表诗人, 以土地与太阳为核心意象, 代表作《大堰河——我的保姆》《我爱这土地》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '艾青');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '顾城', NULL, '男', 1956, 1993, '中国', '朦胧诗派代表诗人, 被称为"童话诗人", 代表作《一代人》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '顾城');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '余光中', NULL, '男', 1928, 2017, '中国', '现当代诗人、散文家, 代表作《乡愁》《白玉苦瓜》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '余光中');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '郑愁予', NULL, '男', 1933, NULL, '中国', '现代派诗人, 代表作《错误》, 被称为"中国的中国诗人"。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '郑愁予');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '席慕蓉', NULL, '女', 1943, NULL, '中国', '当代女诗人、画家, 代表诗集《七里香》《无怨的青春》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '席慕蓉');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '汪国真', NULL, '男', 1956, 2015, '中国', '当代诗人, 诗句清朗励志, 在二十世纪九十年代风靡校园。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '汪国真');

INSERT INTO poet (name, pen_name, gender, birth_year, death_year, nationality, biography)
SELECT '食指', '郭路生', '男', 1948, NULL, '中国', '朦胧诗先驱, 代表作《相信未来》《这是四点零八分的北京》。'
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM poet WHERE name = '食指');

-- ---------- 新增诗歌(13首, 均为节选或短章) ----------
INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '死水',
       '这是一沟绝望的死水，\n清风吹不起半点漪沦。\n不如多扔些破铜烂铁，\n爽性泼你的剩菜残羹。',
       1926, '自由诗',
       '以"一沟绝望的死水"象征沉滞的现实, 是"三美"主张的极致实践, 反讽辛辣而形式整饬。',
       poet_id
FROM poet WHERE name = '闻一多'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '死水');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '教我如何不想她',
       '天上飘着些微云，\n地上吹着些微风。\n啊！微风吹动了我头发，\n教我如何不想她？',
       1920, '自由诗',
       '首创"她"字入诗, 微云、微风的意象层层递进, 思念缠绵而不腻。',
       poet_id
FROM poet WHERE name = '刘半农'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '教我如何不想她');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '成功的花',
       '成功的花，\n人们只惊羡她现时的明艳！\n然而当初她的芽儿，\n浸透了奋斗的泪泉，\n洒遍了牺牲的血雨。',
       1923, '自由诗',
       '以花与芽的对照点明"明艳"背后的奋斗与牺牲, 小诗体隽永。',
       poet_id
FROM poet WHERE name = '冰心'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '成功的花');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '你是人间的四月天',
       '我说你是人间的四月天；\n笑响点亮了四面风；\n轻灵在春的光艳中交舞着变。',
       1934, '自由诗',
       '以四月天喻爱与希望, 意象明丽、节奏轻盈, 是新诗中少有的明朗之作。',
       poet_id
FROM poet WHERE name = '林徽因'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '你是人间的四月天');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '断章',
       '你站在桥上看风景，\n看风景的人在楼上看你。\n明月装饰了你的窗子，\n你装饰了别人的梦。',
       1935, '自由诗',
       '四行之间主客互换, "装饰"二字道尽相对性与人间关联, 言有尽而意无穷。',
       poet_id
FROM poet WHERE name = '卞之琳'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '断章');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '天上的街市',
       '远远的街灯明了，\n好像闪着无数的明星。\n天上的明星现了，\n好像点着无数的街灯。',
       1921, '自由诗',
       '由街灯到明星的联想自然递进, 为理想世界张目, 想象大胆而温暖。',
       poet_id
FROM poet WHERE name = '郭沫若'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '天上的街市');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '我爱这土地',
       '为什么我的眼里常含泪水？\n因为我对这土地爱得深沉……',
       1938, '自由诗',
       '以鸟自喻, 嘶哑的喉咙与深沉的眼泪, 把家国之情推向极致。',
       poet_id
FROM poet WHERE name = '艾青'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '我爱这土地');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '一代人',
       '黑夜给了我黑色的眼睛，\n我却用它寻找光明。',
       1979, '自由诗',
       '两行十字浓缩一代人的觉醒与求索, 是朦胧诗中最具宣言气质的短章。',
       poet_id
FROM poet WHERE name = '顾城'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '一代人');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '乡愁',
       '小时候，\n乡愁是一枚小小的邮票，\n我在这头，\n母亲在那头。\n……\n而现在，\n乡愁是一湾浅浅的海峡，\n我在这头，\n大陆在那头。',
       1972, '自由诗',
       '以邮票、船票、坟墓、海峡四个意象串起人生与家国, 浅语深情。',
       poet_id
FROM poet WHERE name = '余光中'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '乡愁');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '错误',
       '我打江南走过，\n那等在季节里的容颜如莲花的开落。\n……\n我达达的马蹄是美丽的错误，\n我不是归人，是个过客……',
       1954, '自由诗',
       '江南、莲花、马蹄层层铺垫, "美丽的错误"成为现代汉诗的经典修辞。',
       poet_id
FROM poet WHERE name = '郑愁予'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '错误');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '一棵开花的树',
       '如何让你遇见我，\n在我最美丽的时刻。\n为这，\n我已在佛前求了五百年，\n求佛让我们结一段尘缘。',
       1980, '自由诗',
       '以求佛五百年写尽等待的虔诚, 凋零的花瓣是深情最安静的结局。',
       poet_id
FROM poet WHERE name = '席慕蓉'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '一棵开花的树');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '热爱生命',
       '我不去想是否能够成功，\n既然选择了远方，\n便只顾风雨兼程。',
       NULL, '自由诗',
       '排比句式层层推进, "既然选择了远方, 便只顾风雨兼程"影响了一代青年。',
       poet_id
FROM poet WHERE name = '汪国真'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '热爱生命');

INSERT INTO poem (title, content, create_year, form, appreciation, poet_id)
SELECT '相信未来',
       '当蜘蛛网无情地查封了我的炉台，\n当灰烬的余烟叹息着贫困的悲哀，\n我依然固执地铺平失望的灰烬，\n用美丽的雪花写下：相信未来。',
       1968, '自由诗',
       '苦难意象与固执的信念对撞, 开朦胧诗之先声, 激励无数困境中的人。',
       poet_id
FROM poet WHERE name = '食指'
  AND NOT EXISTS (SELECT 1 FROM poem WHERE title = '相信未来');

-- ---------- 新增诗歌的流派归属(INSERT IGNORE: 复合主键防重) ----------
INSERT IGNORE INTO poem_genre (poem_id, genre_id)
SELECT p.poem_id, g.genre_id
FROM poem p
JOIN genre g
WHERE (p.title, g.name) IN
      (('死水', '新月派'),
       ('断章', '现代派'),
       ('我爱这土地', '七月派'),
       ('一代人', '朦胧诗派'));

-- ---------- 新增诗集: 中国新诗百年精选 ----------
INSERT INTO collection (title, publish_year, publisher, introduction)
SELECT '中国新诗百年精选', 2017, '课程演示用', '为课程演示汇编的近现代名篇节选集, 覆盖多个流派与年代。'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM collection WHERE title = '中国新诗百年精选');

INSERT IGNORE INTO collection_poem (collection_id, poem_id, seq_no)
SELECT c.collection_id, p.poem_id, t.seq
FROM (SELECT '我爱这土地' AS ptitle, 1 AS seq
      UNION SELECT '断章', 2
      UNION SELECT '一代人', 3
      UNION SELECT '相信未来', 4
      UNION SELECT '乡愁', 5
      UNION SELECT '你是人间的四月天', 6) t
JOIN poem p ON p.title = t.ptitle
JOIN collection c ON c.title = '中国新诗百年精选';

-- =============================================================
-- 验证(可选):
--   SELECT COUNT(*) AS poets FROM poet;          -- 应为 18
--   SELECT COUNT(*) AS poems FROM poem;          -- 应为 19
--   SELECT COUNT(*) AS genres FROM genre;        -- 应为 5
--   SELECT title, word_count FROM poem WHERE title IN ('死水','断章','一代人');  -- 字数已被触发器填好
--   SELECT title, poet_name, avg_score FROM v_poem_brief ORDER BY create_year;   -- 检索视图可用
--   SELECT title, poem_count FROM v_collection_catalog;
-- =============================================================
