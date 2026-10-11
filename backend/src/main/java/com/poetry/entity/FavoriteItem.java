package com.poetry.entity;

import java.time.LocalDateTime;

/**
 * "我的收藏"列表项: 收藏记录 JOIN 诗歌、诗人后的展示行。
 */
public class FavoriteItem {

    private Long poemId;
    private String title;
    private String poetName;
    private Integer createYear;
    private String form;
    private Double avgScore;
    private String favoriteType;
    private LocalDateTime favoriteTime;

    public Long getPoemId() {
        return poemId;
    }

    public void setPoemId(Long poemId) {
        this.poemId = poemId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getPoetName() {
        return poetName;
    }

    public void setPoetName(String poetName) {
        this.poetName = poetName;
    }

    public Integer getCreateYear() {
        return createYear;
    }

    public void setCreateYear(Integer createYear) {
        this.createYear = createYear;
    }

    public String getForm() {
        return form;
    }

    public void setForm(String form) {
        this.form = form;
    }

    public Double getAvgScore() {
        return avgScore;
    }

    public void setAvgScore(Double avgScore) {
        this.avgScore = avgScore;
    }

    public String getFavoriteType() {
        return favoriteType;
    }

    public void setFavoriteType(String favoriteType) {
        this.favoriteType = favoriteType;
    }

    public LocalDateTime getFavoriteTime() {
        return favoriteTime;
    }

    public void setFavoriteTime(LocalDateTime favoriteTime) {
        this.favoriteTime = favoriteTime;
    }
}
