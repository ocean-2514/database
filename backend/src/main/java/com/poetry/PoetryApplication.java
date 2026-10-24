package com.poetry;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 诗歌信息检索与赏析管理系统 - 服务器端入口。
 * 技术栈: Spring Boot 3 + MyBatis (SQL 全部手写在 resources/mapper/*.xml)。
 */
@SpringBootApplication
@MapperScan("com.poetry.mapper")
public class PoetryApplication {

    public static void main(String[] args) {
        SpringApplication.run(PoetryApplication.class, args);
    }
}
