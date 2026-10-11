package com.poetry.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

/**
 * 密码编码器: 注册时 encode(明文)->哈希, 登录时 matches(明文, 哈希)->校验。
 * BCrypt 每次哈希自动生成随机盐, 同一明文两次结果不同, 但都能通过 matches 验证。
 */
@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
