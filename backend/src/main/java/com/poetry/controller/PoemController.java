package com.poetry.controller;

import com.poetry.common.ApiResponse;
import com.poetry.common.PageResult;
import com.poetry.entity.PoemBrief;
import com.poetry.entity.PoemDetail;
import com.poetry.entity.PoemFulltext;
import com.poetry.service.PoemService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 诗歌接口: 组合检索 / 诗歌详情 / 全文检索。
 */
@RestController
@RequestMapping("/api/poems")
public class PoemController {

    private final PoemService poemService;

    public PoemController(PoemService poemService) {
        this.poemService = poemService;
    }

    /**
     * GET /api/poems?keyword=康桥&poetName=&genre=&yearFrom=&yearTo=&orderBy=&page=1&pageSize=10
     */
    @GetMapping
    public ApiResponse<PageResult<PoemBrief>> search(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String poetName,
            @RequestParam(required = false) String genre,
            @RequestParam(required = false) Integer yearFrom,
            @RequestParam(required = false) Integer yearTo,
            @RequestParam(required = false) Integer orderBy,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize) {
        return ApiResponse.ok(poemService.search(keyword, poetName, genre,
                yearFrom, yearTo, orderBy, page, pageSize));
    }

    /**
     * GET /api/poems/fulltext?keyword=春暖花开
     * (全文检索走存储过程; 需放在 /{poemId} 之前声明避免路径冲突时被误匹配)
     */
    @GetMapping("/fulltext")
    public ApiResponse<List<PoemFulltext>> fulltext(@RequestParam String keyword) {
        return ApiResponse.ok(poemService.fulltextSearch(keyword));
    }

    /**
     * GET /api/poems/1
     */
    @GetMapping("/{poemId}")
    public ApiResponse<PoemDetail> detail(@PathVariable Long poemId) {
        return ApiResponse.ok(poemService.getDetail(poemId));
    }
}
