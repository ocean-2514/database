package com.poetry.mapper;

import com.poetry.entity.FavoriteItem;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 收藏数据访问接口, SQL 见 resources/mapper/FavoriteMapper.xml。
 */
public interface FavoriteMapper {

    /** 查某用户对某诗的收藏记录ID, 未收藏返回 null */
    Long findUserFavorite(@Param("userId") Long userId, @Param("poemId") Long poemId);

    int insertFavorite(@Param("userId") Long userId,
                       @Param("poemId") Long poemId,
                       @Param("favoriteType") String favoriteType);

    int deleteFavorite(@Param("userId") Long userId, @Param("poemId") Long poemId);

    /** 我的收藏(分页), 收藏时间倒序 */
    List<FavoriteItem> listUserFavorites(@Param("userId") Long userId,
                                         @Param("offset") int offset,
                                         @Param("pageSize") int pageSize);

    long countUserFavorites(@Param("userId") Long userId);
}
