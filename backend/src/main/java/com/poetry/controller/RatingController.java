package com.poetry.controller;

import com.poetry.annotation.RequireLogin;
import com.poetry.common.ApiResponse;
import com.poetry.entity.Rating;
import com.poetry.service.RatingService;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 评分接口(全部需要登录)。
 * 动词选择: 评分是"覆盖式写入"(PUT 幂等语义), 与收藏的"仅创建"(POST)区分。
 */
@RestController
public class RatingController {

    private final RatingService ratingService;

    public RatingController(RatingService ratingService) {
        this.ratingService = ratingService;
    }

    /** PUT /api/poems/1/rating?score=4 —— 评分/改分; data: created|updated */
    @PutMapping("/api/poems/{poemId}/rating")
    @RequireLogin
    public ApiResponse<String> rate(@PathVariable Long poemId,
                                    @RequestParam Integer score,
                                    HttpSession session) {
        return ApiResponse.ok(ratingService.rate(
                (Long) session.getAttribute("userId"), poemId, score));
    }

    /** GET /api/poems/1/rating —— 我的评分, 未评过时 data 为 null */
    @GetMapping("/api/poems/{poemId}/rating")
    @RequireLogin
    public ApiResponse<Rating> myRating(@PathVariable Long poemId, HttpSession session) {
        return ApiResponse.ok(ratingService.myRating(
                (Long) session.getAttribute("userId"), poemId));
    }

    /** DELETE /api/poems/1/rating —— 取消评分 */
    @DeleteMapping("/api/poems/{poemId}/rating")
    @RequireLogin
    public ApiResponse<Void> cancel(@PathVariable Long poemId, HttpSession session) {
        ratingService.cancel((Long) session.getAttribute("userId"), poemId);
        return ApiResponse.ok(null);
    }
}
