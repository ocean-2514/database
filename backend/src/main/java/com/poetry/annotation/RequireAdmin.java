package com.poetry.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 标注"需要管理员角色"的接口方法或整个 Controller 类。
 * AuthInterceptor 校验: 未登录 401; 已登录但 role != admin 则 403。
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireAdmin {
}
