package com.poetry.dto;

/**
 * 发表/修改评论的请求体: {"content":"..."}
 */
public class CommentRequest {

    private String content;

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }
}
