package com.poetry.controller;

import com.poetry.annotation.RequireLogin;
import com.poetry.common.ApiResponse;
import com.poetry.common.PageResult;
import com.poetry.entity.FavoriteItem;
import com.poetry.service.FavoriteService;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 收藏接口(全部需要登录, 由 @RequireLogin + AuthInterceptor 保证)。
 * userId 从会话中取, 绝不接受前端传入——否则任何人都能操作别人的收藏。
 */
@RestController
public class FavoriteController {

    private final FavoriteService favoriteService;

    public FavoriteController(FavoriteService favoriteService) {
        this.favoriteService = favoriteService;
    }

    /** POST /api/poems/1/favorite?favoriteType=最爱 */
    @PostMapping("/api/poems/{poemId}/favorite")
    @RequireLogin
    public ApiResponse<Void> add(@PathVariable Long poemId,
                                 @RequestParam(required = false) String favoriteType,
                                 HttpSession session) {
        favoriteService.add((Long) session.getAttribute("userId"), poemId, favoriteType);
        return ApiResponse.ok(null);
    }

    /** DELETE /api/poems/1/favorite */
    @DeleteMapping("/api/poems/{poemId}/favorite")
    @RequireLogin
    public ApiResponse<Void> cancel(@PathVariable Long poemId, HttpSession session) {
        favoriteService.cancel((Long) session.getAttribute("userId"), poemId);
        return ApiResponse.ok(null);
    }

    /** GET /api/favorites?page=1&pageSize=10 —— 我的收藏 */
    @GetMapping("/api/favorites")
    @RequireLogin
    public ApiResponse<PageResult<FavoriteItem>> list(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            HttpSession session) {
        return ApiResponse.ok(favoriteService.list(
                (Long) session.getAttribute("userId"), page, pageSize));
    }
}
