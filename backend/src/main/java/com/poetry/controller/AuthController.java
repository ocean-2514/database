package com.poetry.controller;

import com.poetry.common.ApiResponse;
import com.poetry.dto.LoginRequest;
import com.poetry.dto.RegisterRequest;
import com.poetry.dto.UserView;
import com.poetry.service.AuthService;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 认证接口: 注册 / 登录 / 当前用户 / 登出。
 * HttpSession 由 Spring 注入; 登录成功后浏览器凭 Cookie 在后续请求中找回同一会话。
 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /** POST /api/auth/register, 请求体 JSON */
    @PostMapping("/register")
    public ApiResponse<UserView> register(@RequestBody RegisterRequest req) {
        return ApiResponse.ok(authService.register(req));
    }

    /** POST /api/auth/login, 请求体 JSON; 成功后 Set-Cookie 下发 JSESSIONID */
    @PostMapping("/login")
    public ApiResponse<UserView> login(@RequestBody LoginRequest req, HttpSession session) {
        return ApiResponse.ok(authService.login(req, session));
    }

    /** GET /api/auth/me: 未登录时 data 为 null */
    @GetMapping("/me")
    public ApiResponse<UserView> me(HttpSession session) {
        return ApiResponse.ok(authService.currentUser(session));
    }

    /** POST /api/auth/logout */
    @PostMapping("/logout")
    public ApiResponse<Void> logout(HttpSession session) {
        authService.logout(session);
        return ApiResponse.ok(null);
    }
}
