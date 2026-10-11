package com.poetry.config;

import com.poetry.annotation.RequireAdmin;
import com.poetry.annotation.RequireLogin;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * 登录/角色校验拦截器: 请求到达 Controller 之前执行 preHandle。
 * @RequireLogin —— 未登录返回 401;
 * @RequireAdmin —— 未登录 401, 已登录但非管理员 403。
 * 未标注的接口默认公开。
 */
public class AuthInterceptor implements HandlerInterceptor {

    private static void deny(HttpServletResponse response, int status, String message) throws Exception {
        response.setStatus(status);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"code\":" + status + ",\"message\":\"" + message + "\",\"data\":null}");
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        // 非 Controller 方法(如静态资源)放行
        if (!(handler instanceof HandlerMethod handlerMethod)) {
            return true;
        }
        RequireAdmin requireAdmin = handlerMethod.getMethodAnnotation(RequireAdmin.class);
        if (requireAdmin == null) {
            // 类级标注(如整个 AdminController)同样生效
            requireAdmin = handlerMethod.getBeanType().getAnnotation(RequireAdmin.class);
        }
        if (requireAdmin != null) {
            HttpSession session = request.getSession();
            if (session.getAttribute("userId") == null) {
                deny(response, 401, "请先登录");
                return false;
            }
            if (!"admin".equals(session.getAttribute("role"))) {
                deny(response, 403, "需要管理员权限");
                return false;
            }
            return true;
        }
        // 未标注 @RequireLogin 的接口默认公开(浏览/检索不要求登录)
        if (handlerMethod.getMethodAnnotation(RequireLogin.class) == null) {
            return true;
        }
        HttpSession session = request.getSession();
        if (session.getAttribute("userId") != null) {
            return true;
        }
        deny(response, 401, "请先登录");
        return false;
    }
}
