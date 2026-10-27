package com.poetry.service;

import com.poetry.entity.Rating;
import com.poetry.mapper.PoemMapper;
import com.poetry.mapper.RatingMapper;
import org.springframework.stereotype.Service;

/**
 * 评分业务: 评分/改分/查我的评分/取消评分。
 * 应用层校验分值范围, 数据库端 CHECK (score BETWEEN 1 AND 5) 约束校验。
 * 平均分不落库, 由查询实时计算(v_poem_brief 等)——评分变化无需维护任何统计列。
 */
@Service
public class RatingService {

    private final RatingMapper ratingMapper;
    private final PoemMapper poemMapper;

    public RatingService(RatingMapper ratingMapper, PoemMapper poemMapper) {
        this.ratingMapper = ratingMapper;
        this.poemMapper = poemMapper;
    }

    /** 评分/改分: 返回 "created"(首次) 或 "updated"(改分) */
    public String rate(Long userId, Long poemId, Integer score) {
        if (score == null || score < 1 || score > 5) {
            throw new IllegalArgumentException("评分需为 1-5 的整数");
        }
        if (poemMapper.countPoemById(poemId) == 0) {
            throw new IllegalArgumentException("诗歌不存在: id=" + poemId);
        }
        int rows = ratingMapper.upsert(userId, poemId, score);
        return rows == 1 ? "created" : "updated";
    }

    /** 当前用户对某诗的评分, 未评过返回 null */
    public Rating myRating(Long userId, Long poemId) {
        return ratingMapper.findByUserAndPoem(userId, poemId);
    }

    public void cancel(Long userId, Long poemId) {
        if (ratingMapper.findByUserAndPoem(userId, poemId) == null) {
            throw new IllegalArgumentException("尚未评分");
        }
        ratingMapper.deleteRating(userId, poemId);
    }
}
