package com.poetry.entity;

/**
 * 流派: 检索筛选下拉框数据源。
 */
public class Genre {

    private Long genreId;
    private String name;
    private String description;

    public Long getGenreId() {
        return genreId;
    }

    public void setGenreId(Long genreId) {
        this.genreId = genreId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
