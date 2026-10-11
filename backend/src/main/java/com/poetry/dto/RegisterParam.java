package com.poetry.dto;

/**
 * 调用存储过程 sp_register_user 的参数载体。
 * userId 声明为 OUT 模式: 存储过程执行后, MyBatis 把新用户ID回填到这个字段。
 */
public class RegisterParam {

    private String username;
    private String passwordHash;
    private String email;
    private Long userId;      // OUT: 由存储过程回填

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

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }
}
