package com.poetry.dto;

import com.poetry.entity.User;

import java.time.LocalDateTime;

/**
 * 返回给前端的用户信息: 不含 passwordHash, 是 User 的"对外视图"。
 */
public class UserView {

    private Long userId;
    private String username;
    private String email;
    private String role;
    private String status;
    private LocalDateTime registerTime;

    public static UserView from(User u) {
        UserView v = new UserView();
        v.userId = u.getUserId();
        v.username = u.getUsername();
        v.email = u.getEmail();
        v.role = u.getRole();
        v.status = u.getStatus();
        v.registerTime = u.getRegisterTime();
        return v;
    }

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
