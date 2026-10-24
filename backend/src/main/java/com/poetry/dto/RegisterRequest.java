package com.poetry.dto;

/**
 * 注册请求体。前端以 JSON 提交: {"username":"...","password":"...","email":"..."}
 * password 明文仅在请求处理过程中短暂存在, 入库前转换为 BCrypt 哈希。
 */
public class RegisterRequest {

    private String username;
    private String password;
    private String email;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
