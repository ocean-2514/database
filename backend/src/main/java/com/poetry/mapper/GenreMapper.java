package com.poetry.mapper;

import com.poetry.entity.Genre;

import java.util.List;

/**
 * 流派数据访问接口, SQL 见 resources/mapper/GenreMapper.xml。
 */
public interface GenreMapper {

    List<Genre> listGenres();
}
