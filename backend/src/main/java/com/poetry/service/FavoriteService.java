package com.poetry.service;

import com.poetry.common.PageResult;
import com.poetry.entity.FavoriteItem;
import com.poetry.mapper.FavoriteMapper;
import com.poetry.mapper.PoemMapper;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 收藏业务: 添加 / 取消 / 我的收藏(分页)。
 * 防重复的两道防线: 应用层预查(友好提示) + poem_favorite 表 UNIQUE(user_id, poem_id)(数据库层保证)。
 */
@Service
public class FavoriteService {

    private final FavoriteMapper favoriteMapper;
    private final PoemMapper poemMapper;

    public FavoriteService(FavoriteMapper favoriteMapper, PoemMapper poemMapper) {
        this.favoriteMapper = favoriteMapper;
        this.poemMapper = poemMapper;
    }

    public void add(Long userId, Long poemId, String favoriteType) {
        if (poemMapper.countPoemById(poemId) == 0) {
            throw new IllegalArgumentException("诗歌不存在或已下架: id=" + poemId);
        }
        if (favoriteMapper.findUserFavorite(userId, poemId) != null) {
            throw new IllegalArgumentException("已收藏过该诗歌");
        }
        String type = (favoriteType == null || favoriteType.isBlank()) ? "默认" : favoriteType.trim();
        favoriteMapper.insertFavorite(userId, poemId, type);
    }

    public void cancel(Long userId, Long poemId) {
        if (favoriteMapper.findUserFavorite(userId, poemId) == null) {
            throw new IllegalArgumentException("尚未收藏该诗歌");
        }
        favoriteMapper.deleteFavorite(userId, poemId);
    }

    public PageResult<FavoriteItem> list(Long userId, Integer page, Integer pageSize) {
        int p = (page == null || page < 1) ? 1 : page;
        int size = (pageSize == null || pageSize < 1) ? 10 : Math.min(pageSize, 50);
        long total = favoriteMapper.countUserFavorites(userId);
        List<FavoriteItem> list = total == 0
                ? List.of()
                : favoriteMapper.listUserFavorites(userId, (p - 1) * size, size);
        return PageResult.of(total, p, size, list);
    }
}
