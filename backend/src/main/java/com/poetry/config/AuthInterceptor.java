package com.poetry.config;

import com.poetry.annotation.RequireLogin;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * 登录校验拦截器: 请求到达 Controller 之前执行 preHandle。
 * 只对标注了 @RequireLogin 的接口方法生效; 未登录时以 401 JSON 短路响应。
 */
public class AuthInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        // 非 Controller 方法(如静态资源)放行
        if (!(handler instanceof HandlerMethod handlerMethod)) {
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
        response.setStatus(401);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"code\":401,\"message\":\"请先登录\",\"data\":null}");
        return false;
    }
}
