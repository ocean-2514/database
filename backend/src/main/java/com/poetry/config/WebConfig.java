package com.poetry.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web 配置: 跨域放行 + 登录校验拦截器。
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOriginPatterns("http://localhost:5173", "http://localhost:3000")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowCredentials(true);   // 允许携带 Cookie(会话需要)
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // 拦截器覆盖所有 /api/** 请求, 但只对标注 @RequireLogin 的方法生效
        registry.addInterceptor(new AuthInterceptor()).addPathPatterns("/api/**");
    }
}
