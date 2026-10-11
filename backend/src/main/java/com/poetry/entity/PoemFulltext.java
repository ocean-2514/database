package com.poetry.entity;

/**
 * 全文检索结果项: 由存储过程 sp_fulltext_search_poems 返回。
 */
public class PoemFulltext {

    private Long poemId;
    private String title;
    private Integer createYear;
    private Double relevance;    // MATCH...AGAINST 相关度, 越大越相关

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

    public Integer getCreateYear() {
        return createYear;
    }

    public void setCreateYear(Integer createYear) {
        this.createYear = createYear;
    }

    public Double getRelevance() {
        return relevance;
    }

    public void setRelevance(Double relevance) {
        this.relevance = relevance;
    }
}
