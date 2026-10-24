package com.poetry.mapper;

import com.poetry.entity.Rating;
import org.apache.ibatis.annotations.Param;

/**
 * 评分数据访问接口, SQL 见 resources/mapper/RatingMapper.xml。
 */
public interface RatingMapper {

    Rating findByUserAndPoem(@Param("userId") Long userId, @Param("poemId") Long poemId);

    /** 评分/改分: 覆盖式写入, 返回受影响行数(1=新增, 2=更新) */
    int upsert(@Param("userId") Long userId,
               @Param("poemId") Long poemId,
               @Param("score") Integer score);

    int deleteRating(@Param("userId") Long userId, @Param("poemId") Long poemId);
}
