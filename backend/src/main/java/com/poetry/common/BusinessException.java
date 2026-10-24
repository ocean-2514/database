package com.poetry.common;

/**
 * 带业务状态码的异常: 403 无权操作 / 404 资源不存在 等。
 * GlobalExceptionHandler 会把 code 原样返回给前端。
 */
public class BusinessException extends RuntimeException {

    private final int code;

    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }

    public int getCode() {
        return code;
    }
}
