package com.poetry.entity;

import java.time.LocalDateTime;

/**
 * 评论列表展示项: 评论 JOIN 用户(取用户名)后的展示行, 不含 userId 等内部字段。
 */
public class CommentItem {

    private Long commentId;
    private String username;
    private String content;
    private Integer likeCount;
    private LocalDateTime commentTime;

    public Long getCommentId() {
        return commentId;
    }

    public void setCommentId(Long commentId) {
        this.commentId = commentId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public Integer getLikeCount() {
        return likeCount;
    }

    public void setLikeCount(Integer likeCount) {
        this.likeCount = likeCount;
    }

    public LocalDateTime getCommentTime() {
        return commentTime;
    }

    public void setCommentTime(LocalDateTime commentTime) {
        this.commentTime = commentTime;
    }
}
