# 04 SQL 与运行结果素材

> 对应《系统实现报告》第三、四章。所有"运行结果"均为本项目实测的真实接口响应/数据库查询输出，报告中可直接粘贴 JSON 或截图。完整 SQL 见 `sql/` 各脚本与 `backend/src/main/resources/mapper/*.xml`。

## 一、基本表的定义

10 张表完整 DDL 见 `sql/01_create_database.sql`（建库）、`sql/02_create_tables.sql`（建表+约束）。命名约定：`fk_` 外键、`uk_` 唯一、`chk_` 检查、`idx_` 普通索引。报告正文中建议给出 2 个代表性完整 DDL（核心表 poem + 联系实体 rating），其余以表格摘要呈现：

**poem（核心实体，节选）**

```sql
CREATE TABLE poem (
    poem_id      BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '诗歌ID',
    title        VARCHAR(100)      NOT NULL COMMENT '标题',
    content      MEDIUMTEXT        NOT NULL COMMENT '正文',
    create_year  SMALLINT UNSIGNED NULL COMMENT '创作年份',
    form         VARCHAR(20)       NULL COMMENT '体裁',
    word_count   INT UNSIGNED      NOT NULL DEFAULT 0 COMMENT '字数(触发器维护)',
    appreciation TEXT              NULL COMMENT '赏析',
    poet_id      BIGINT UNSIGNED   NOT NULL COMMENT '所属诗人',
    PRIMARY KEY (poem_id),
    KEY idx_poem_title (title),
    KEY idx_poem_year (create_year),
    CONSTRAINT fk_poem_poet FOREIGN KEY (poet_id) REFERENCES poet (poet_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='诗歌表';
```

**rating（联系实体，含 CHECK 与 UNIQUE）**

```sql
CREATE TABLE rating (
    rating_id   BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    user_id     BIGINT UNSIGNED  NOT NULL,
    poem_id     BIGINT UNSIGNED  NOT NULL,
    score       TINYINT UNSIGNED NOT NULL COMMENT '评分(1-5)',
    rating_time DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (rating_id),
    UNIQUE KEY uk_rating_user_poem (user_id, poem_id),
    CONSTRAINT chk_rating_score CHECK (score BETWEEN 1 AND 5),
    CONSTRAINT fk_rating_user FOREIGN KEY (user_id) REFERENCES `user` (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rating_poem FOREIGN KEY (poem_id) REFERENCES poem (poem_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评分记录表';
```

## 二、触发器的设计与实现说明（5 个）

| 触发器 | 时机 | 作用 | 经应用验证的方式 |
| --- | --- | --- | --- |
| trg_poem_word_count_bi | BEFORE INSERT ON poem | 字数 = 正文字符数 | 管理端新增《天上的街市》后详情接口返回 `wordCount=36` |
| trg_poem_word_count_bu | BEFORE UPDATE ON poem | 正文变化时重算字数（`<=>` NULL 安全比较） | 管理端修改正文后字数自动更新 |
| trg_poet_bd | BEFORE DELETE ON poet | 名下仍有诗歌则 SIGNAL 拒绝 | 删除有作品的诗人返回 400："删除被数据库规则拦截: 该诗人名下仍有诗歌作品，禁止删除(请先处理其作品)" |
| trg_user_bd | BEFORE DELETE ON user | 管理员账户禁止删除 | 直接 SQL 验证（应用层无删除用户功能） |
| trg_rating_bi | BEFORE INSERT ON rating | 评分时间不得晚于当前时间 | 构造未来时间 INSERT 被拒 |

代码节选（字数维护，`sql/05_triggers.sql`）：

```sql
CREATE TRIGGER trg_poem_word_count_bu
BEFORE UPDATE ON poem
FOR EACH ROW
BEGIN
    IF NOT (NEW.content <=> OLD.content) THEN
        SET NEW.word_count = CHAR_LENGTH(NEW.content);
    END IF;
END
```

## 三、存储过程的设计与实现说明（4 个）

| 存储过程 | 参数 | 逻辑要点 | 经应用验证的方式 |
| --- | --- | --- | --- |
| sp_search_poems | 5 个检索条件 + 排序方式 + 页码/页大小 | 条件全部可空（NULL 即忽略）；两个结果集（总数+当前页）；动态 ORDER BY | 亦可由后端等价的动态 SQL 实现分页检索（见 §四.1） |
| sp_fulltext_search_poems | 关键词 | MATCH...AGAINST 自然语言模式，按相关度排序 | `GET /api/poems/fulltext` |
| sp_register_user | 用户名/密码哈希/邮箱 + OUT 新用户ID | 查重后插入，重名 SIGNAL | `POST /api/auth/register` |
| sp_add_collection_with_poems | 诗集字段 + 逗号分隔 poemIds | **显式事务**：START TRANSACTION → 插诗集 → 循环建收录 → COMMIT；异常 ROLLBACK+RESIGNAL | `POST /api/admin/collections` |

事务验证实录（无效诗 ID 999 → 外键报错 → 整体回滚，目录中无残留诗集）：

```
POST /api/admin/collections {"title":"回滚测试诗集","poemIds":"1,999"}
→ {"code":400,"message":"诗集创建失败(已整体回滚): Cannot add or update a child row:
   a foreign key constraint fails (`poetry_db`.`collection_poem` ...)"}
```

## 四、各功能 SQL 与实测运行结果

> 每条功能给出：请求 → SQL 出处 → 实测响应。SQL 均为手写原生 SQL（MyBatis XML）。

### 1. 组合检索（多表连接 + 动态条件 + 分页）

```
GET /api/poems?keyword=康桥
```
SQL（`PoemMapper.xml` searchPoems，poem JOIN poet + 相关子查询统计 + LIMIT 分页）：
```sql
SELECT p.poem_id, p.title, pt.name AS poet_name, ..., 
       IFNULL((SELECT ROUND(AVG(r.score),1) FROM rating r WHERE r.poem_id = p.poem_id),0) AS avg_score, ...
FROM poem p JOIN poet pt ON pt.poet_id = p.poet_id
WHERE (p.title LIKE CONCAT('%',?,'%') OR p.content LIKE CONCAT('%',?,'%'))
ORDER BY p.poem_id DESC LIMIT ?, ?
```
实测响应：
```json
{"code":200,"message":"success","data":{"total":1,"page":1,"pageSize":10,"list":[
  {"poemId":1,"title":"再别康桥","poetName":"徐志摩","createYear":1928,"form":"自由诗",
   "wordCount":68,"avgScore":5.0,"ratingCount":1,"commentCount":1,"favoriteCount":1}]}}
```

### 2. 中文全文检索（存储过程 + ngram 索引）

```
GET /api/poems/fulltext?keyword=春暖花开
```
```sql
{CALL sp_fulltext_search_poems(?)}
```
实测：命中《面朝大海，春暖花开》，相关度 3.63；数据扩充后搜"黑夜 光明"命中《一代人》相关度 6.54。

### 3. 诗歌详情（视图/外模式）

```
GET /api/poems/1
```
```sql
SELECT * FROM v_poem_detail WHERE poem_id = ?
```
实测：一次查询返回诗歌+作者（生卒年）+流派（新月派）+平均分/评论数/收藏数聚合。

### 4. 用户认证（BCrypt + 存储过程 OUT 参数 + 会话）

- 注册：`POST /api/auth/register` → `CALL sp_register_user(?,?,?,?)`（OUT 回填）→ 返回 `{"userId":4,...,"role":"reader"}`
- 重复注册 → `{"code":400,"message":"用户名已存在"}`；密码过短 → 400
- 登录成功响应头：`Set-Cookie: JSESSIONID=333530CB...; Path=/; HttpOnly`
- 错误密码/不存在用户 → 同一提示 `{"code":400,"message":"用户名或密码错误"}`（防枚举）
- 未登录访问受保护接口 → `401 {"code":401,"message":"请先登录"}`

### 5. 收藏（防重复双保险 + 401）

未登录 → 401；收藏诗 1 → 200；重复收藏 → `400 已收藏过该诗歌`；收藏不存在的诗 999 → `400 诗歌不存在`；我的收藏列表含标题/作者/平均分/收藏类型；取消后列表为空，再取消 → 400。

### 6. 评分（ON DUPLICATE KEY 覆盖写 + 平均分联动）

```
PUT /api/poems/1/rating?score=3   →  data:"updated"（首次为 created）
```
```sql
INSERT INTO rating (user_id, poem_id, score) VALUES (?,?,?)
ON DUPLICATE KEY UPDATE score = ?, rating_time = CURRENT_TIMESTAMP
```
平均分联动实测（平均分在查询时计算，无需维护统计列）：

| 时点 | GET /api/poems/1 的 avgScore |
| --- | --- |
| 评分前（种子数据 reader1 评 5 分） | 5.0 |
| testuser 评 3 分后 | 4.0（=(5+3)/2） |
| 取消评分后 | 5.0 |

非法分值 score=9 → 400"评分需为 1-5 的整数"（应用校验 + CHECK 约束双保险）；score=abc → 400"参数类型不正确"。

### 7. 评论（资源级权限 403/404 + 公开读）

- 发表 → 200 返回 `{"commentId":4}`（useGeneratedKeys 回填）；空内容 → 400
- 用户 B 修改/删除用户 A 的评论 → `403 只能操作自己的评论`
- 改/删不存在的评论 → `404 评论不存在`
- 未登录读列表 → 200（公开读），按评论时间倒序 JOIN 用户名

### 8. 管理端（@RequireAdmin + 触发器 + 事务）

- 未登录 → 401；读者访问 → `403 需要管理员权限`
- 新增诗歌不写字数列 → 详情返回 `wordCount=36`（触发器填充）
- 删除有作品的诗人 → 400（触发器 SIGNAL 文本直达前端）
- 诗集含无效诗 ID → 400 + 事务回滚（目录无残留）
- 流派重名 → `400 流派名称已存在`（UNIQUE）
- 下架诗歌 → 200，评分/评论/收藏/流派关系经外键级联清除

## 五、测试场景汇总

| 模块 | 场景数 | 覆盖要点 |
| --- | --- | --- |
| 认证 | 9 | 注册/查重/校验/登录/错误密码/防枚举/会话/登出 |
| 收藏 | 9 | 401/收藏/重复/不存在/列表/取消/空列表 |
| 评分 | 12 | created/updated/越界/类型错误/不存在/我的评分/联动/取消/401 |
| 评论 | 11 | 发表/空内容/404/401/公开读/属主 403/改/删/再删 |
| 管理 | 19 | 401/403/四实体 CRUD/触发器拦截/事务回滚/UNIQUE/级联 |
| 合计 | **约 60** | 全部通过 |
