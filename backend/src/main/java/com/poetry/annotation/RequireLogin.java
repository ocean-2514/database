package com.poetry.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 标注"需要登录才能访问"的接口方法。
 * AuthInterceptor 检测到该注解时校验 Session, 未登录直接返回 401, 不进入 Controller。
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireLogin {
}
