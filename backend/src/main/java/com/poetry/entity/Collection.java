package com.poetry.entity;

/**
 * 诗集表 collection 的一行映射; poemCount 仅在查目录视图 v_collection_catalog 时有值。
 * poemIds 字段仅用于调用存储过程 sp_add_collection_with_poems 的入参载体。
 */
public class Collection {

    private Long collectionId;
    private String title;
    private Integer publishYear;
    private String publisher;
    private String isbn;
    private String introduction;
    private Integer poemCount;   // 视图字段, 表里没有
    private String poemIds;      // 逗号分隔的诗歌ID串, 仅新增时使用

    public Long getCollectionId() {
        return collectionId;
    }

    public void setCollectionId(Long collectionId) {
        this.collectionId = collectionId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public Integer getPublishYear() {
        return publishYear;
    }

    public void setPublishYear(Integer publishYear) {
        this.publishYear = publishYear;
    }

    public String getPublisher() {
        return publisher;
    }

    public void setPublisher(String publisher) {
        this.publisher = publisher;
    }

    public String getIsbn() {
        return isbn;
    }

    public void setIsbn(String isbn) {
        this.isbn = isbn;
    }

    public String getIntroduction() {
        return introduction;
    }

    public void setIntroduction(String introduction) {
        this.introduction = introduction;
    }

    public Integer getPoemCount() {
        return poemCount;
    }

    public void setPoemCount(Integer poemCount) {
        this.poemCount = poemCount;
    }

    public String getPoemIds() {
        return poemIds;
    }

    public void setPoemIds(String poemIds) {
        this.poemIds = poemIds;
    }
}
