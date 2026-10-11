package com.poetry.common;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常处理: 任何异常都转成统一的 JSON 响应, 前端不必处理裸错误页。
 * 完整异常堆栈打印到服务端控制台——浏览器里看到的 message 只是摘要。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /** 业务校验失败(如页码非法、诗歌不存在) */
    @ExceptionHandler(IllegalArgumentException.class)
    public ApiResponse<Void> handleBadRequest(IllegalArgumentException e) {
        log.warn("请求参数错误: {}", e.getMessage());
        return ApiResponse.error(400, e.getMessage());
    }

    /** 兜底: 数据库异常、未预期异常等 */
    @ExceptionHandler(Exception.class)
    public ApiResponse<Void> handleOther(Exception e) {
        log.error("服务器内部错误", e);
        return ApiResponse.error(500, "服务器内部错误: " + e.getMessage());
    }
}
