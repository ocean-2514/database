package com.poetry.controller;

import com.poetry.annotation.RequireLogin;
import com.poetry.common.ApiResponse;
import com.poetry.common.PageResult;
import com.poetry.dto.CommentRequest;
import com.poetry.entity.CommentItem;
import com.poetry.service.CommentService;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * 评论接口: 读公开, 写需登录, 改删校验属主。
 */
@RestController
public class CommentController {

    private final CommentService commentService;

    public CommentController(CommentService commentService) {
        this.commentService = commentService;
    }

    /** GET /api/poems/1/comments?page=1&pageSize=10 —— 公开 */
    @GetMapping("/api/poems/{poemId}/comments")
    public ApiResponse<PageResult<CommentItem>> list(@PathVariable Long poemId,
                                                     @RequestParam(defaultValue = "1") Integer page,
                                                     @RequestParam(defaultValue = "10") Integer pageSize) {
        return ApiResponse.ok(commentService.list(poemId, page, pageSize));
    }

    /** POST /api/poems/1/comments, 请求体 {"content":"..."} —— 需登录 */
    @PostMapping("/api/poems/{poemId}/comments")
    @RequireLogin
    public ApiResponse<Map<String, Long>> add(@PathVariable Long poemId,
                                              @RequestBody CommentRequest req,
                                              HttpSession session) {
        long commentId = commentService.add((Long) session.getAttribute("userId"), poemId, req);
        return ApiResponse.ok(Map.of("commentId", commentId));
    }

    /** PUT /api/comments/5, 请求体 {"content":"..."} —— 仅属主 */
    @PutMapping("/api/comments/{commentId}")
    @RequireLogin
    public ApiResponse<Void> edit(@PathVariable Long commentId,
                                  @RequestBody CommentRequest req,
                                  HttpSession session) {
        commentService.edit((Long) session.getAttribute("userId"), commentId, req);
        return ApiResponse.ok(null);
    }

    /** DELETE /api/comments/5 —— 属主或管理员 */
    @DeleteMapping("/api/comments/{commentId}")
    @RequireLogin
    public ApiResponse<Void> delete(@PathVariable Long commentId, HttpSession session) {
        commentService.delete((Long) session.getAttribute("userId"),
                (String) session.getAttribute("role"), commentId);
        return ApiResponse.ok(null);
    }
}
