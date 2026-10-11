# E-R 图说明

本目录存放《诗歌信息检索与赏析管理系统》的 E-R 图源文件。

| 文件 | 说明 |
| --- | --- |
| `诗歌系统ER图.drawio` | draw.io 源文件，3 页：初步 E-R 图、基本 E-R 图（诗歌域）、基本 E-R 图（用户域） |
| `gen_er_drawio.py` | 生成脚本，修改实体/属性/联系定义后重新运行 `python gen_er_drawio.py` 即可再生成 |
| `ER图说明.md` | 本文件：记法说明、Mermaid 版关系图、联系→关系模式映射 |

## 一、如何查看与编辑

1. 打开 [app.diagrams.net](https://app.diagrams.net)（或 draw.io 桌面版 / VS Code 插件 "Draw.io Integration"），打开 `诗歌系统ER图.drawio`；
2. 拖动元素微调布局后，`文件 → 导出为 → PNG`（建议缩放 200%，白底）插入报告；
3. 若增删属性，优先改 `gen_er_drawio.py` 中实体定义再重新生成，保持脚本与图一致。

记法（Chen）：矩形 = 实体，菱形 = 联系，椭圆 = 属性，**下划线 = 主键**，边上 1 / n / m = 联系类型。
基本 E-R 图拆为"诗歌域 / 用户域"两页绘制，报告中说明两页合并即完整基本 E-R 图。

## 二、实体与属性（8 个实体，现代诗歌口径）

| 实体 | 属性（下划线为主键） |
| --- | --- |
| 诗人 | <u>poet_id</u>、姓名、笔名、性别、生年、卒年、国籍、简介 |
| 诗歌 | <u>poem_id</u>、标题、正文、创作年份、体裁、字数、赏析 |
| 诗集 | <u>collection_id</u>、诗集名称、出版年份、出版社、ISBN、简介 |
| 流派 | <u>genre_id</u>、流派名称、描述 |
| 用户 | <u>user_id</u>、用户名、密码、邮箱、角色、注册时间、账户状态 |
| 评分记录 | <u>rating_id</u>、评分、评分时间 |
| 评论 | <u>comment_id</u>、评论内容、评论时间、点赞数 |
| 收藏记录 | <u>favorite_id</u>、收藏时间、收藏类型 |

约定：评分记录 / 评论 / 收藏记录是**联系实体**，其 user_id、poem_id 通过与"用户""诗歌"的联系表达，不作为属性重复画出；"字数"由触发器依据正文自动维护（反范式冗余，报告中需说明）；流派举例为新月派、现代派、朦胧诗派、九叶诗派等现代诗歌流派。

## 三、联系（9 个）

| 联系 | 两端 | 类型 | 落表方式 |
| --- | --- | --- | --- |
| 创作 | 诗人 — 诗歌 | 1 : n | 诗歌表外键 poet_id |
| 收录 | 诗集 — 诗歌 | m : n | 关联表 collection_poem（含篇目序号） |
| 属于 | 诗歌 — 流派 | m : n | 关联表 poem_genre |
| 评分(用户/诗歌) | 用户、诗歌 — 评分记录 | 各 1 : n | rating 表外键 user_id、poem_id，UNIQUE(user_id, poem_id) 防重复评分 |
| 评论(用户/诗歌) | 用户、诗歌 — 评论 | 各 1 : n | comment 表外键 |
| 收藏(用户/诗歌) | 用户、诗歌 — 收藏记录 | 各 1 : n | favorite 表外键，UNIQUE(user_id, poem_id) 防重复收藏 |

## 四、Mermaid 版（逻辑结构速览，含关联表）

> 渲染前注意：Mermaid 需 v10.3+（支持 `实体["中文别名"]`）。IDEA Markdown 预览、GitHub、[mermaid.live](https://mermaid.live) 均可渲染。

```mermaid
erDiagram
    POET["诗人"] ||--o{ POEM["诗歌"] : "创作"
    POEM["诗歌"] }o--o{ GENRE["流派"] : "属于"
    POEM_GENRE["诗歌-流派"] }o--|| POEM["诗歌"] : ""
    POEM_GENRE["诗歌-流派"] }o--|| GENRE["流派"] : ""
    COLLECTION["诗集"] }o--o{ POEM["诗歌"] : "收录"
    COLLECTION_POEM["诗集-诗歌"] }o--|| COLLECTION["诗集"] : ""
    COLLECTION_POEM["诗集-诗歌"] }o--|| POEM["诗歌"] : ""
    USER["用户"] ||--o{ RATING["评分记录"] : "提交"
    POEM["诗歌"] ||--o{ RATING["评分记录"] : "获得"
    USER["用户"] ||--o{ COMMENT["评论"] : "发表"
    POEM["诗歌"] ||--o{ COMMENT["评论"] : "获得"
    USER["用户"] ||--o{ FAVORITE["收藏记录"] : "收藏"
    POEM["诗歌"] ||--o{ FAVORITE["收藏记录"] : "获得"

    POET {
        bigint poet_id PK
        varchar name "姓名"
        varchar pen_name "笔名"
        enum gender "性别"
        smallint birth_year "生年"
        smallint death_year "卒年"
        varchar nationality "国籍"
        text biography "简介"
    }
    POEM {
        bigint poem_id PK
        varchar title "标题"
        mediumtext content "正文"
        smallint create_year "创作年份"
        varchar form "体裁"
        int word_count "字数(触发器维护)"
        text appreciation "赏析"
        bigint poet_id FK
    }
    GENRE {
        bigint genre_id PK
        varchar name "流派名称"
        varchar description "描述"
    }
    COLLECTION {
        bigint collection_id PK
        varchar title "诗集名称"
        smallint publish_year "出版年份"
        varchar publisher "出版社"
        varchar isbn "ISBN"
        text introduction "简介"
    }
    USER {
        bigint user_id PK
        varchar username "用户名"
        varchar password_hash "密码哈希"
        varchar email "邮箱"
        enum role "角色"
        enum status "账户状态"
        datetime register_time "注册时间"
    }
    RATING {
        bigint rating_id PK
        bigint user_id FK "UNIQUE(user_id,poem_id)"
        bigint poem_id FK
        tinyint score "评分1-5"
        datetime rating_time "评分时间"
    }
    COMMENT {
        bigint comment_id PK
        bigint user_id FK
        bigint poem_id FK
        text content "评论内容"
        datetime comment_time "评论时间"
        int like_count "点赞数"
    }
    FAVORITE {
        bigint favorite_id PK
        bigint user_id FK "UNIQUE(user_id,poem_id)"
        bigint poem_id FK
        datetime favorite_time "收藏时间"
        varchar favorite_type "收藏类型"
    }
    POEM_GENRE {
        bigint poem_id PK "复合主键"
        bigint genre_id PK "复合主键"
    }
    COLLECTION_POEM {
        bigint collection_id PK "复合主键"
        bigint poem_id PK "复合主键"
        smallint seq_no "篇目序号"
    }
```

## 五、联系 → 关系模式（逻辑设计的过渡）

8 个实体 + 2 个 m:n 联系 = **10 个关系模式**：

1. 诗人(<u>poet_id</u>, 姓名, 笔名, 性别, 生年, 卒年, 国籍, 简介)
2. 诗歌(<u>poem_id</u>, 标题, 正文, 创作年份, 体裁, 字数, 赏析, *poet_id*)
3. 诗集(<u>collection_id</u>, 诗集名称, 出版年份, 出版社, ISBN, 简介)
4. 流派(<u>genre_id</u>, 流派名称, 描述)
5. 用户(<u>user_id</u>, 用户名, 密码, 邮箱, 角色, 注册时间, 账户状态)
6. 评分记录(<u>rating_id</u>, *user_id*, *poem_id*, 评分, 评分时间)
7. 评论(<u>comment_id</u>, *user_id*, *poem_id*, 评论内容, 评论时间, 点赞数)
8. 收藏记录(<u>favorite_id</u>, *user_id*, *poem_id*, 收藏时间, 收藏类型)
9. 诗歌-流派(<u>*poem_id*, *genre_id*</u>)
10. 诗集-诗歌(<u>*collection_id*, *poem_id*</u>, 篇目序号)

3NF 判定要点（写报告用）：

- 各模式非主属性对码完全函数依赖（无复合主键上的部分依赖）→ 2NF；
- 诗歌模式中"字数"函数依赖于"正文"（可由正文计算），对码存在传递依赖，属**有意的反范式冗余**，由触发器 `trg_poem_word_count_*` 维护一致性，换取列表页免于实时计算；若坚持严格 3NF 可去掉字数列改为查询时计算；
- 其余模式中不存在 非主属性 → 非主属性 的传递依赖（如诗歌表只存 poet_id 不存诗人姓名）→ 3NF；
- 评分记录、收藏记录上 (user_id, poem_id) 唯一约束保证同一用户对同一首诗只有一条评分/收藏。
