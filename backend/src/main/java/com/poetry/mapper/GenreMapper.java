package com.poetry.mapper;

import com.poetry.entity.Genre;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 流派数据访问接口, SQL 见 resources/mapper/GenreMapper.xml。
 */
public interface GenreMapper {

    List<Genre> listGenres();

    /** 管理端: 新增, useGeneratedKeys 回填主键到 genre.genreId */
    int insert(Genre genre);

    int update(Genre genre);

    int deleteById(@Param("genreId") Long genreId);
}
