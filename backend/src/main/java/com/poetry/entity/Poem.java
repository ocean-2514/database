package com.poetry.entity;

/**
 * 诗歌表 poem 的一行映射, 兼作管理员新增/修改的请求体。
 * wordCount 只读: 插入/更新不写该列, 由触发器依据正文自动维护。
 */
public class Poem {

    private Long poemId;
    private String title;
    private String content;
    private Integer createYear;
    private String form;
    private Integer wordCount;
    private String appreciation;
    private Long poetId;

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

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
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

    public Integer getWordCount() {
        return wordCount;
    }

    public void setWordCount(Integer wordCount) {
        this.wordCount = wordCount;
    }

    public String getAppreciation() {
        return appreciation;
    }

    public void setAppreciation(String appreciation) {
        this.appreciation = appreciation;
    }

    public Long getPoetId() {
        return poetId;
    }

    public void setPoetId(Long poetId) {
        this.poetId = poetId;
    }
}
