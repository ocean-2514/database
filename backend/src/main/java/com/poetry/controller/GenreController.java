package com.poetry.controller;

import com.poetry.common.ApiResponse;
import com.poetry.entity.Genre;
import com.poetry.service.GenreService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 流派接口: 检索页筛选下拉框数据源。
 */
@RestController
@RequestMapping("/api/genres")
public class GenreController {

    private final GenreService genreService;

    public GenreController(GenreService genreService) {
        this.genreService = genreService;
    }

    /**
     * GET /api/genres
     */
    @GetMapping
    public ApiResponse<List<Genre>> list() {
        return ApiResponse.ok(genreService.listAll());
    }
}
