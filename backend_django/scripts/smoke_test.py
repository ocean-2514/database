"""33 个接口的端到端回归测试。

运行前先初始化测试库：
    DB_PASSWORD=... bash scripts/init_test_db.sh
    DB_PASSWORD=... DB_NAME=poetry_db_test uv run python scripts/smoke_test.py

脚本只会对名字以 _test 结尾的数据库执行写操作。
"""
import json
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import urlencode

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poetry_backend.settings")

import django

django.setup()

import logging

# 预期的 401/403 分支会被 Django 记为 warning，测试时关闭以减少噪音
logging.getLogger("django.request").setLevel(logging.ERROR)

from django.conf import settings
from django.db import connection
from django.test import Client


class Checker:
    def __init__(self):
        self.passed = 0
        self.failed: list[str] = []

    def check(self, condition, label):
        if condition:
            self.passed += 1
        else:
            self.failed.append(label)
            print(f"  FAIL: {label}")

    def eq(self, actual, expected, label):
        self.check(actual == expected, f"{label}: expected {expected!r}, got {actual!r}")


C = Checker()


def body(response):
    try:
        return response.json()
    except Exception:
        return {"raw": response.content.decode("utf-8", "replace")[:500]}


def expect_ok(response, label):
    payload = body(response)
    C.eq(response.status_code, 200, f"{label} HTTP")
    C.eq(payload.get("code"), 200, f"{label} code")
    if payload.get("code") != 200:
        print(f"  -> {label}: {payload}")
    return payload.get("data")


def expect_error(response, code, label, http_status=200, contains=None):
    payload = body(response)
    C.eq(response.status_code, http_status, f"{label} HTTP")
    C.eq(payload.get("code"), code, f"{label} code")
    if contains is not None:
        C.check(
            contains in (payload.get("message") or ""),
            f"{label} message contains {contains!r}, got {payload.get('message')!r}",
        )
    return payload


def jpost(client, path, payload):
    return client.post(path, data=json.dumps(payload), content_type="application/json")


def jput(client, path, payload):
    return client.put(path, data=json.dumps(payload), content_type="application/json")


def q(path, **params):
    return path + "?" + urlencode(params)


def register_and_login(username, password="reader123", email=None):
    email = email or f"{username}@example.com"
    client = Client()
    data = expect_ok(
        jpost(client, "/api/auth/register", {
            "username": username,
            "password": password,
            "email": email,
        }),
        f"register {username}",
    )
    expect_ok(
        jpost(client, "/api/auth/login", {"username": username, "password": password}),
        f"login {username}",
    )
    return client, data


def main():
    db_name = settings.DATABASES["default"]["NAME"]
    if not db_name.endswith("_test"):
        print(f"拒绝执行：当前数据库 {db_name!r} 不是测试库（需以 _test 结尾）")
        return 2

    print(f"使用测试库: {db_name}")
    suffix = uuid.uuid4().hex[:8]
    anon = Client()

    # ---------------- 公开接口 ----------------
    print("[1/6] 公开检索 / 详情 / 全文检索 / 流派")
    search = expect_ok(anon.get("/api/poems", {"page": 1, "pageSize": 5}), "GET /api/poems")
    C.eq(set(search.keys()), {"total", "page", "pageSize", "list"}, "分页字段")
    C.eq(search["page"], 1, "page")
    C.eq(search["pageSize"], 5, "pageSize")
    C.check(search["total"] >= 6, "种子数据总数 >= 6")
    C.check(len(search["list"]) == 5, "第一页返回 5 条")
    first = search["list"][0]
    C.eq(
        set(first.keys()),
        {
            "poemId", "title", "poetName", "createYear", "form", "wordCount",
            "avgScore", "ratingCount", "commentCount", "favoriteCount",
        },
        "PoemBrief 字段",
    )
    poem_id = first["poemId"]

    by_keyword = expect_ok(anon.get("/api/poems", {"keyword": "再别康桥"}), "关键词检索")
    C.check(any(item["title"] == "再别康桥" for item in by_keyword["list"]), "关键词命中")
    by_poet = expect_ok(anon.get("/api/poems", {"poetName": "徐志摩"}), "诗人检索")
    C.check(by_poet["total"] >= 2, "徐志摩至少 2 首")
    by_genre = expect_ok(anon.get("/api/poems", {"genre": "新月派"}), "流派检索")
    C.check(by_genre["total"] >= 2, "新月派至少 2 首")
    by_year = expect_ok(anon.get("/api/poems", {"yearFrom": 1980}), "年份检索")
    C.check(
        all(item["createYear"] is None or item["createYear"] >= 1980 for item in by_year["list"]),
        "yearFrom 过滤",
    )
    by_title = expect_ok(anon.get("/api/poems", {"orderBy": 2, "pageSize": 50}), "标题排序")
    titles = [item["title"] for item in by_title["list"]]
    C.eq(titles, sorted(titles), "orderBy=2 标题升序")
    by_score = expect_ok(anon.get("/api/poems", {"orderBy": 1, "pageSize": 50}), "评分排序")
    scores = [item["avgScore"] for item in by_score["list"]]
    C.eq(scores, sorted(scores, reverse=True), "orderBy=1 平均分降序")
    capped = expect_ok(anon.get("/api/poems", {"pageSize": 100}), "pageSize 上限")
    C.eq(capped["pageSize"], 50, "pageSize 上限为 50")
    defaulted = expect_ok(anon.get("/api/poems", {"pageSize": 0}), "pageSize 归一下限")
    C.eq(defaulted["pageSize"], 10, "pageSize<1 时回落到 10")

    # CORS：原前端地址允许携带 Cookie 的预检，其他来源拒绝
    preflight = anon.options(
        "/api/poems",
        HTTP_ORIGIN="http://localhost:5173",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="Content-Type",
    )
    C.eq(preflight.status_code, 200, "CORS 预检 HTTP")
    C.eq(
        preflight["Access-Control-Allow-Origin"], "http://localhost:5173",
        "CORS 允许来源",
    )
    C.eq(preflight["Access-Control-Allow-Credentials"], "true", "CORS 允许 Cookie")
    blocked = anon.options(
        "/api/poems",
        HTTP_ORIGIN="http://evil.example.com",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
    )
    C.eq(blocked.status_code, 403, "CORS 拒绝未知来源")
    unknown = anon.get("/api/does-not-exist")
    C.eq(unknown.status_code, 404, "未知 API 路径 HTTP")
    C.eq(body(unknown).get("code"), 404, "未知 API 路径 code")

    expect_error(anon.get("/api/poems/99999999"), 400, "不存在的诗歌详情", contains="诗歌不存在或已下架")

    fulltext = expect_ok(anon.get("/api/poems/fulltext", {"keyword": "康桥"}), "全文检索")
    C.check(isinstance(fulltext, list) and len(fulltext) >= 1, "全文检索有结果")
    C.eq(set(fulltext[0].keys()), {"poemId", "title", "createYear", "relevance"}, "全文检索字段")
    expect_error(anon.get("/api/poems/fulltext"), 400, "全文检索缺少 keyword")
    expect_error(anon.get("/api/poems/fulltext", {"keyword": "   "}), 400, "全文检索空白 keyword")

    detail = expect_ok(anon.get(f"/api/poems/{poem_id}"), "诗歌详情")
    C.eq(
        set(detail.keys()),
        {
            "poemId", "title", "content", "createYear", "form", "wordCount",
            "appreciation", "poetId", "poetName", "penName", "birthYear",
            "deathYear", "genres", "avgScore", "commentCount", "favoriteCount",
        },
        "PoemDetail 字段",
    )

    genres = expect_ok(anon.get("/api/genres"), "流派列表")
    C.check(len(genres) >= 4, "种子流派 >= 4")
    C.eq(set(genres[0].keys()), {"genreId", "name", "description"}, "Genre 字段")

    # ---------------- 认证 ----------------
    print("[2/6] 注册 / 登录 / me / 登出")
    C.eq(expect_ok(anon.get("/api/auth/me"), "匿名 me"), None, "匿名 me data=null")

    seed_reader = Client()
    seed_login = jpost(
        seed_reader, "/api/auth/login", {"username": "reader1", "password": "reader123"}
    )
    seed_data = expect_ok(seed_login, "种子 reader1 登录")
    C.check("JSESSIONID" in seed_login.cookies, "登录下发 JSESSIONID Cookie")
    C.eq(seed_data["username"], "reader1", "种子用户名")
    C.eq(seed_data["role"], "user", "种子角色")
    C.check("passwordHash" not in seed_data, "不返回密码哈希")

    cors_login = Client().post(
        "/api/auth/login",
        data=json.dumps({"username": "reader2", "password": "reader123"}),
        content_type="application/json",
        HTTP_ORIGIN="http://localhost:5173",
    )
    C.eq(cors_login.status_code, 200, "带 Origin 的登录 HTTP")
    C.eq(
        cors_login["Access-Control-Allow-Origin"], "http://localhost:5173",
        "实际响应 CORS 来源",
    )
    vary = cors_login.get("Vary", "")
    C.check(
        "Origin" in vary and "Cookie" in vary,
        f"CORS 与 Cookie 的 Vary 均保留，实际 {vary!r}",
    )

    temp_admin = Client()
    expect_ok(
        jpost(temp_admin, "/api/auth/login", {"username": "admin", "password": "admin123"}),
        "临时管理员登录",
    )
    expect_ok(temp_admin.post("/api/auth/logout"), "临时管理员登出")
    C.eq(expect_ok(temp_admin.get("/api/auth/me"), "登出后 me"), None, "登出后会话失效")

    username1 = f"smoke_{suffix}_a"
    reader, user_data = register_and_login(username1)
    C.eq(user_data["role"], "user", "新用户角色")
    C.eq(
        set(user_data.keys()),
        {"userId", "username", "email", "role", "status", "registerTime"},
        "UserView 字段",
    )
    me_data = expect_ok(reader.get("/api/auth/me"), "登录后 me")
    C.eq(me_data["username"], username1, "me 用户名")

    expect_error(
        jpost(anon, "/api/auth/register", {
            "username": username1, "password": "reader123", "email": f"{username1}x@example.com",
        }),
        400, "重复用户名", contains="用户名已存在",
    )
    expect_error(
        jpost(anon, "/api/auth/register", {
            "username": f"smoke_{suffix}_dup", "password": "reader123",
            "email": f"{username1}@example.com",
        }),
        400, "重复邮箱", contains="用户名或邮箱已存在",
    )
    expect_error(
        jpost(anon, "/api/auth/register", {
            "username": f"smoke_{suffix}_mail", "password": "reader123", "email": "bad-email",
        }),
        400, "邮箱格式", contains="邮箱格式不正确",
    )
    expect_error(
        jpost(anon, "/api/auth/register", {
            "username": f"smoke_{suffix}_pwd", "password": "123", "email": f"pwd_{suffix}@example.com",
        }),
        400, "密码长度", contains="密码长度需为 6-64 个字符",
    )
    expect_error(
        jpost(anon, "/api/auth/login", {"username": username1, "password": "wrong-password"}),
        400, "错误密码", contains="用户名或密码错误",
    )

    disabled_name = f"smoke_{suffix}_disabled"
    disabled = Client()
    disabled_data = expect_ok(
        jpost(disabled, "/api/auth/register", {
            "username": disabled_name, "password": "reader123",
            "email": f"{disabled_name}@example.com",
        }),
        "注册待停用用户",
    )
    with connection.cursor() as cursor:
        cursor.execute("UPDATE app_user SET account_status = 'disabled' WHERE user_id = %s",
                       [disabled_data["userId"]])
    expect_error(
        jpost(disabled, "/api/auth/login", {"username": disabled_name, "password": "reader123"}),
        400, "停用账户登录", contains="账户已被停用",
    )

    username2 = f"smoke_{suffix}_b"
    reader2, _ = register_and_login(username2)

    # ---------------- 互动 ----------------
    print("[3/6] 收藏 / 评分 / 评论")
    favorite_path = f"/api/poems/{poem_id}/favorite"
    expect_ok(reader.post(q(favorite_path, favoriteType="最爱")), "添加收藏")
    expect_error(reader.post(q(favorite_path, favoriteType="最爱")), 400, "重复收藏", contains="已收藏过该诗歌")
    favorites = expect_ok(reader.get("/api/favorites", {"page": 1, "pageSize": 10}), "我的收藏")
    C.check(favorites["total"] >= 1, "收藏总数 >= 1")
    favorite_item = next(item for item in favorites["list"] if item["poemId"] == poem_id)
    C.eq(favorite_item["favoriteType"], "最爱", "收藏类型")
    C.eq(
        set(favorite_item.keys()),
        {
            "poemId", "title", "poetName", "createYear", "form",
            "avgScore", "favoriteType", "favoriteTime",
        },
        "FavoriteItem 字段",
    )
    expect_ok(reader.delete(favorite_path), "取消收藏")
    expect_error(reader.delete(favorite_path), 400, "重复取消收藏", contains="尚未收藏该诗歌")

    rating_path = f"/api/poems/{poem_id}/rating"
    C.eq(expect_ok(reader.put(q(rating_path, score=5)), "首次评分"), "created", "首次评分状态")
    rating = expect_ok(reader.get(rating_path), "查询我的评分")
    C.eq(rating["score"], 5, "评分值")
    C.eq(
        set(rating.keys()),
        {"ratingId", "userId", "poemId", "score", "ratingTime"},
        "Rating 字段",
    )
    C.eq(expect_ok(reader.put(q(rating_path, score=4)), "修改评分"), "updated", "修改评分状态")
    C.eq(expect_ok(reader.get(rating_path), "再次查询评分")["score"], 4, "修改后评分值")
    expect_error(reader.put(q(rating_path, score=6)), 400, "非法评分", contains="评分需为 1-5 的整数")
    expect_ok(reader.delete(rating_path), "取消评分")
    C.eq(expect_ok(reader.get(rating_path), "取消后查询评分"), None, "取消后 data=null")
    expect_error(reader.delete(rating_path), 400, "重复取消评分", contains="尚未评分")

    comments_path = f"/api/poems/{poem_id}/comments"
    comment_data = expect_ok(
        jpost(reader, comments_path, {"content": f"烟测试评论 {suffix}"}),
        "发表评论",
    )
    comment_id = comment_data["commentId"]
    comments = expect_ok(anon.get(comments_path, {"page": 1, "pageSize": 10}), "评论列表")
    C.check(any(item["commentId"] == comment_id for item in comments["list"]), "评论列表包含新评论")
    C.eq(
        set(comments["list"][0].keys()),
        {"commentId", "username", "content", "likeCount", "commentTime"},
        "CommentItem 字段",
    )
    expect_ok(
        jput(reader, f"/api/comments/{comment_id}", {"content": f"烟测试评论已修改 {suffix}"}),
        "修改自己的评论",
    )
    expect_error(
        jput(reader2, f"/api/comments/{comment_id}", {"content": "越权修改"}),
        403, "修改他人评论", contains="只能操作自己的评论",
    )
    expect_ok(
        jpost(reader2, comments_path, {"content": f"待管理员删除 {suffix}"}),
        "reader2 发表评论",
    )
    comments2 = expect_ok(anon.get(comments_path, {"page": 1, "pageSize": 50}), "获取评论找 reader2 评论")
    reader2_comment = next(
        item for item in comments2["list"] if item["username"] == username2
    )
    admin = Client()
    expect_ok(
        jpost(admin, "/api/auth/login", {"username": "admin", "password": "admin123"}),
        "管理员登录",
    )
    expect_ok(admin.delete(f"/api/comments/{reader2_comment['commentId']}"), "管理员删除他人评论")

    # 未登录 / 越权
    expect_error(anon.post(favorite_path), 401, "匿名收藏", http_status=401, contains="请先登录")
    expect_error(anon.get("/api/favorites"), 401, "匿名收藏列表", http_status=401)
    expect_error(anon.put(q(rating_path, score=5)), 401, "匿名评分", http_status=401)
    expect_error(anon.post(comments_path), 401, "匿名评论", http_status=401)
    expect_error(anon.put(f"/api/comments/{comment_id}", {"content": "x"}),
                 401, "匿名修改评论", http_status=401)
    expect_error(anon.delete(f"/api/comments/{comment_id}"), 401, "匿名删除评论", http_status=401)
    expect_error(
        reader.put(q("/api/poems/99999999/rating", score=5)),
        400, "给不存在诗歌评分", contains="诗歌不存在或已下架",
    )
    expect_error(
        reader.post("/api/poems/99999999/favorite"),
        400, "收藏不存在诗歌", contains="诗歌不存在或已下架",
    )
    expect_error(
        jpost(reader, "/api/poems/99999999/comments", {"content": "x"}),
        400, "评论不存在诗歌", contains="诗歌不存在或已下架",
    )
    expect_error(
        jput(reader, "/api/comments/99999999", {"content": "x"}),
        404, "修改不存在评论", contains="评论不存在",
    )
    expect_error(reader.delete("/api/comments/99999999"), 404, "删除不存在评论", contains="评论不存在")
    expect_error(anon.get("/api/admin/poets"), 401, "匿名管理端", http_status=401, contains="请先登录")
    expect_error(
        reader.get("/api/admin/poets"), 403, "普通用户管理端",
        http_status=403, contains="需要管理员权限",
    )

    # ---------------- 管理端 ----------------
    print("[4/6] 诗人 / 流派管理")
    poets = expect_ok(admin.get("/api/admin/poets"), "诗人列表")
    C.check(len(poets) >= 5, "种子诗人 >= 5")
    C.eq(
        set(poets[0].keys()),
        {"poetId", "name", "penName", "gender", "birthYear", "deathYear", "nationality", "biography"},
        "Poet 字段",
    )
    seed_poet_id = poets[0]["poetId"]
    expect_error(
        admin.delete(f"/api/admin/poets/{seed_poet_id}"), 400,
        "删除有作品的诗人", contains="删除被数据库规则拦截",
    )

    new_poet_data = expect_ok(
        jpost(admin, "/api/admin/poets", {
            "name": f"烟测试诗人{suffix}",
            "penName": "烟测试",
            "gender": "女",
            "birthYear": 1900,
            "deathYear": 1980,
            "nationality": "中国",
            "biography": "接口测试数据",
        }),
        "新增诗人",
    )
    new_poet_id = new_poet_data["poetId"]
    expect_ok(
        jput(admin, f"/api/admin/poets/{new_poet_id}", {
            "name": f"烟测试诗人{suffix}改",
            "penName": "烟测试",
            "gender": "女",
            "birthYear": 1900,
            "deathYear": 1980,
            "nationality": "中国",
            "biography": "接口测试数据",
        }),
        "修改诗人",
    )
    expect_ok(admin.delete(f"/api/admin/poets/{new_poet_id}"), "删除无作品诗人")
    expect_error(
        jpost(admin, "/api/admin/poets", {"name": "   "}),
        400, "诗人姓名必填", contains="诗人姓名不能为空",
    )

    genre_name = f"烟测试流派{suffix}"
    genre_data = expect_ok(jpost(admin, "/api/admin/genres", {"name": genre_name, "description": "测试"}), "新增流派")
    genre_id = genre_data["genreId"]
    expect_ok(
        jput(admin, f"/api/admin/genres/{genre_id}", {"name": genre_name + "改", "description": "测试改"}),
        "修改流派",
    )
    expect_error(
        jpost(admin, "/api/admin/genres", {"name": genre_name + "改"}),
        400, "重复流派", contains="流派名称已存在",
    )
    expect_ok(admin.delete(f"/api/admin/genres/{genre_id}"), "删除流派")
    expect_error(
        jput(admin, f"/api/admin/genres/{genre_id}", {"name": "不存在"}),
        404, "修改不存在流派", contains="流派不存在",
    )

    print("[5/6] 诗集 / 诗歌管理")
    collections = expect_ok(admin.get("/api/admin/collections"), "诗集列表")
    C.check(len(collections) >= 3, "种子诗集 >= 3")
    C.eq(
        set(collections[0].keys()),
        {"collectionId", "title", "publishYear", "publisher", "isbn", "introduction", "poemCount", "poemIds"},
        "Collection 字段",
    )
    C.eq(collections[0]["poemIds"], None, "Collection.poemIds=null")

    collection_title = f"烟测试诗集{suffix}"
    expect_ok(
        jpost(admin, "/api/admin/collections", {
            "title": collection_title,
            "publicationYear": 2020,
            "publisher": "烟测试出版社",
            "isbn": None,
            "introduction": "接口测试",
            "poemIds": str(poem_id),
        }),
        "新增诗集（存储过程）",
    )
    collections = expect_ok(admin.get("/api/admin/collections"), "诗集列表（新增后）")
    collection = next(item for item in collections if item["title"] == collection_title)
    collection_id = collection["collectionId"]
    C.check(collection["poemCount"] >= 1, "诗集收录数")
    expect_ok(
        jput(admin, f"/api/admin/collections/{collection_id}", {
            "title": collection_title + "改",
            "publicationYear": 2020,
            "publisher": "烟测试出版社",
            "isbn": None,
            "introduction": "接口测试改",
        }),
        "修改诗集",
    )
    bad_title = f"烟测试坏诗集{suffix}"
    expect_error(
        jpost(admin, "/api/admin/collections", {
            "title": bad_title,
            "publicationYear": 2020,
            "publisher": "烟测试出版社",
            "isbn": None,
            "introduction": "应整体回滚",
            "poemIds": "99999999",
        }),
        400, "无效诗歌ID创建诗集", contains="诗集创建失败(已整体回滚)",
    )
    collections = expect_ok(admin.get("/api/admin/collections"), "诗集列表（回滚后）")
    C.check(not any(item["title"] == bad_title for item in collections), "坏诗集整体回滚")
    expect_ok(admin.delete(f"/api/admin/collections/{collection_id}"), "删除诗集")

    poem_data = expect_ok(
        jpost(admin, "/api/admin/poems", {
            "title": f"烟测试诗{suffix}",
            "content": "第一行\n第二行",
            "createYear": 2024,
            "form": "自由诗",
            "appreciation": "测试赏析",
            "poetId": seed_poet_id,
        }),
        "新增诗歌",
    )
    new_poem_id = poem_data["poemId"]
    new_detail = expect_ok(anon.get(f"/api/poems/{new_poem_id}"), "新诗详情")
    C.eq(new_detail["wordCount"], len("第一行\n第二行"), "字数派生")
    expect_ok(
        jput(admin, f"/api/admin/poems/{new_poem_id}", {
            "title": f"烟测试诗{suffix}改",
            "content": "第一行\n第二行\n第三行",
            "createYear": 2024,
            "form": "自由诗",
            "appreciation": "测试赏析改",
            "poetId": seed_poet_id,
        }),
        "修改诗歌",
    )
    expect_ok(admin.put(q(f"/api/admin/poems/{new_poem_id}/status", value="withdrawn")), "下架诗歌")
    expect_error(anon.get(f"/api/poems/{new_poem_id}"), 400, "下架后详情", contains="诗歌不存在或已下架")
    expect_error(
        admin.put(q(f"/api/admin/poems/{new_poem_id}/status", value="bad")),
        400, "非法发布状态", contains="发布状态只能是 published 或 withdrawn",
    )
    expect_ok(admin.put(q(f"/api/admin/poems/{new_poem_id}/status", value="published")), "恢复诗歌")
    expect_ok(anon.get(f"/api/poems/{new_poem_id}"), "恢复后详情")

    # 有互动记录的诗歌不能物理删除
    expect_ok(reader.post(q(f"/api/poems/{new_poem_id}/favorite")), "为新诗添加收藏")
    expect_ok(reader.put(q(f"/api/poems/{new_poem_id}/rating", score=5)), "为新诗评分")
    expect_ok(jpost(reader, f"/api/poems/{new_poem_id}/comments", {"content": "新诗评论"}), "为新诗评论")
    expect_error(
        admin.delete(f"/api/admin/poems/{new_poem_id}"), 400,
        "删除有互动记录的诗歌", contains="删除被数据库规则拦截",
    )

    # 无互动的诗歌可以物理删除
    fresh_poem = expect_ok(
        jpost(admin, "/api/admin/poems", {
            "title": f"烟测试可删诗{suffix}",
            "content": "可删除",
            "poetId": seed_poet_id,
        }),
        "新增可删除诗歌",
    )
    fresh_id = fresh_poem["poemId"]
    expect_ok(admin.delete(f"/api/admin/poems/{fresh_id}"), "物理删除无互动诗歌")
    expect_error(admin.delete(f"/api/admin/poems/{fresh_id}"), 404, "重复删除诗歌", contains="诗歌不存在")

    expect_error(
        jpost(admin, "/api/admin/poems", {"content": "缺少标题", "poetId": seed_poet_id}),
        400, "诗歌标题必填", contains="诗歌标题不能为空",
    )
    expect_error(
        jpost(admin, "/api/admin/poems", {
            "title": "不存在诗人", "content": "正文", "poetId": 99999999,
        }),
        404, "诗人不存在", contains="诗人不存在",
    )

    # ---------------- 汇总 ----------------
    print("[6/6] 汇总")
    total = C.passed + len(C.failed)
    print(f"通过 {C.passed}/{total} 项断言")
    if C.failed:
        print("失败项：")
        for item in C.failed:
            print(" -", item)
        return 1
    print("全部接口回归通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
