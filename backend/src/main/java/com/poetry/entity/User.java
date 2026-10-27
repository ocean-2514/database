package com.poetry.entity;

import java.time.LocalDateTime;

/**
 * 用户表 `user` 的一行映射。
 * passwordHash 是 BCrypt 哈希串, 任何情况下都不应返回给前端。
 */
public class User {

    private Long userId;
    private String username;
    private String passwordHash;
    private String email;
    private String role;        // reader / admin
    private String status;      // active / banned
    private LocalDateTime registerTime;

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public LocalDateTime getRegisterTime() {
        return registerTime;
    }

    public void setRegisterTime(LocalDateTime registerTime) {
        this.registerTime = registerTime;
    }
}
