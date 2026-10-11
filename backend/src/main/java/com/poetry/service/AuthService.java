package com.poetry.service;

import com.poetry.dto.LoginRequest;
import com.poetry.dto.RegisterParam;
import com.poetry.dto.RegisterRequest;
import com.poetry.dto.UserView;
import com.poetry.entity.User;
import com.poetry.mapper.UserMapper;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * 认证业务: 注册 / 登录 / 当前用户 / 登出。
 *
 * 注册链路有三层校验: 应用层参数校验、服务层用户名预查重、
 * 数据库端存储过程查重与 UNIQUE 约束。
 */
@Service
public class AuthService {

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    public AuthService(UserMapper userMapper, PasswordEncoder passwordEncoder) {
        this.userMapper = userMapper;
        this.passwordEncoder = passwordEncoder;
    }

    public UserView register(RegisterRequest req) {
        // 1. 应用层校验
        String username = req.getUsername() == null ? "" : req.getUsername().trim();
        if (username.length() < 2 || username.length() > 30) {
            throw new IllegalArgumentException("用户名长度需为 2-30 个字符");
        }
        String password = req.getPassword() == null ? "" : req.getPassword();
        if (password.length() < 6 || password.length() > 64) {
            throw new IllegalArgumentException("密码长度需为 6-64 个字符");
        }
        String email = req.getEmail() == null ? "" : req.getEmail().trim();
        if (!email.isEmpty() && !email.matches("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")) {
            throw new IllegalArgumentException("邮箱格式不正确");
        }

        // 2. 用户名预查重, 给出友好提示; 并发场景由存储过程查重与 UNIQUE 约束保证
        if (userMapper.findByUsername(username) != null) {
            throw new IllegalArgumentException("用户名已存在");
        }

        // 3. BCrypt 哈希(自动加盐), 数据库中不保存明文密码
        RegisterParam param = new RegisterParam();
        param.setUsername(username);
        param.setPasswordHash(passwordEncoder.encode(password));
        param.setEmail(email.isEmpty() ? null : email);

        userMapper.register(param);   // 调存储过程, 新用户ID回填到 param.userId
        User user = userMapper.findByUsername(username);
        return UserView.from(user);
    }

    public UserView login(LoginRequest req, jakarta.servlet.http.HttpSession session) {
        User user = userMapper.findByUsername(
                req.getUsername() == null ? "" : req.getUsername().trim());
        // 用户不存在与密码错误给出同一句提示, 避免攻击者借此枚举有效用户名
        if (user == null
                || !passwordEncoder.matches(
                        req.getPassword() == null ? "" : req.getPassword(),
                        user.getPasswordHash())) {
            throw new IllegalArgumentException("用户名或密码错误");
        }
        if ("banned".equals(user.getStatus())) {
            throw new IllegalArgumentException("账户已被封禁");
        }

        // 登录成功: 用户身份写入会话, 后续请求凭 Cookie(JSESSIONID) 找回
        session.setAttribute("userId", user.getUserId());
        session.setAttribute("username", user.getUsername());
        session.setAttribute("role", user.getRole());
        return UserView.from(user);
    }

    /** 未登录返回 null(前端据此判断是否已登录) */
    public UserView currentUser(jakarta.servlet.http.HttpSession session) {
        Object userId = session.getAttribute("userId");
        if (userId == null) {
            return null;
        }
        User user = userMapper.findByUserId((Long) userId);
        return user == null ? null : UserView.from(user);
    }

    public void logout(jakarta.servlet.http.HttpSession session) {
        session.invalidate();   // 服务端销毁会话, 旧 Cookie 立即失效
    }
}
