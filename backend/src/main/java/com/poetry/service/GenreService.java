package com.poetry.service;

import com.poetry.entity.Genre;
import com.poetry.mapper.GenreMapper;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 流派业务逻辑: 供检索页筛选下拉框使用。
 */
@Service
public class GenreService {

    private final GenreMapper genreMapper;

    public GenreService(GenreMapper genreMapper) {
        this.genreMapper = genreMapper;
    }

    public List<Genre> listAll() {
        return genreMapper.listGenres();
    }
}
