package com.poetry.mapper;

import com.poetry.entity.Poet;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 诗人数据访问接口(管理端), SQL 见 resources/mapper/PoetMapper.xml。
 */
public interface PoetMapper {

    List<Poet> listAll();

    long countById(@Param("poetId") Long poetId);

    /** 新增, useGeneratedKeys 回填自增主键到 poet.poetId */
    int insert(Poet poet);

    int update(Poet poet);

    int deleteById(@Param("poetId") Long poetId);
}
