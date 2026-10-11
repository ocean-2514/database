package com.poetry.entity;

import java.time.LocalDateTime;

/**
 * 评分记录表 rating 的一行映射。
 */
public class Rating {

    private Long ratingId;
    private Long userId;
    private Long poemId;
    private Integer score;      // 1-5, CHECK 约束校验
    private LocalDateTime ratingTime;

    public Long getRatingId() {
        return ratingId;
    }

    public void setRatingId(Long ratingId) {
        this.ratingId = ratingId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getPoemId() {
        return poemId;
    }

    public void setPoemId(Long poemId) {
        this.poemId = poemId;
    }

    public Integer getScore() {
        return score;
    }

    public void setScore(Integer score) {
        this.score = score;
    }

    public LocalDateTime getRatingTime() {
        return ratingTime;
    }

    public void setRatingTime(LocalDateTime ratingTime) {
        this.ratingTime = ratingTime;
    }
}
