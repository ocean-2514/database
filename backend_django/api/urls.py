"""33 个接口的路由表。

路径顺序与原 Spring Controller 一致；fulltext 必须放在 /poems/{id} 之前。
"""
from django.urls import path, re_path

from .views import (
    admin_views,
    auth_views,
    comment_views,
    errors,
    favorite_views,
    poem_views,
    rating_views,
)

urlpatterns = [
    # 检索
    path("poems", poem_views.search),
    path("poems/fulltext", poem_views.fulltext),
    path("poems/<str:poem_id>", poem_views.detail),
    path("genres", poem_views.genres),

    # 认证
    path("auth/register", auth_views.register),
    path("auth/login", auth_views.login),
    path("auth/me", auth_views.me),
    path("auth/logout", auth_views.logout),

    # 收藏
    path("poems/<str:poem_id>/favorite", favorite_views.favorite),
    path("favorites", favorite_views.my_favorites),

    # 评分
    path("poems/<str:poem_id>/rating", rating_views.rating),

    # 评论
    path("poems/<str:poem_id>/comments", comment_views.comments),
    path("comments/<str:comment_id>", comment_views.comment_detail),

    # 管理端 - 诗人
    path("admin/poets", admin_views.poets),
    path("admin/poets/<str:poet_id>", admin_views.poet_detail),

    # 管理端 - 诗歌
    path("admin/poems", admin_views.poems),
    path("admin/poems/<str:poem_id>/status", admin_views.poem_status),
    path("admin/poems/<str:poem_id>", admin_views.poem_detail),

    # 管理端 - 诗集
    path("admin/collections", admin_views.collections),
    path("admin/collections/<str:collection_id>", admin_views.collection_detail),

    # 管理端 - 流派
    path("admin/genres", admin_views.genres),
    path("admin/genres/<str:genre_id>", admin_views.genre_detail),

    # 未匹配的 /api/ 路径统一返回 JSON 404
    re_path(r"^.*$", errors.api_not_found),
]
