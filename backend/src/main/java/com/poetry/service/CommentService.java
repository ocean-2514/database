package com.poetry.service;

import com.poetry.common.BusinessException;
import com.poetry.common.PageResult;
import com.poetry.dto.CommentRequest;
import com.poetry.entity.Comment;
import com.poetry.entity.CommentItem;
import com.poetry.mapper.CommentMapper;
import com.poetry.mapper.PoemMapper;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 评论业务: 发表 / 修改 / 删除 / 按诗分页查看。
 * 权限模型(写报告可直接引用):
 *   端点级  —— @RequireLogin 拦截器挡住未登录用户(401)
 *   资源级  —— Service 校验评论属主, 非属主 403; 管理员可删除任意评论
 *   读接口公开 —— 浏览未登录也可看评论, 只有写操作要求登录
 */
@Service
public class CommentService {

    private static final int MAX_CONTENT_LENGTH = 1000;

    private final CommentMapper commentMapper;
    private final PoemMapper poemMapper;

    public CommentService(CommentMapper commentMapper, PoemMapper poemMapper) {
        this.commentMapper = commentMapper;
        this.poemMapper = poemMapper;
    }

    /** 发表评论, 返回新评论ID */
    public long add(Long userId, Long poemId, CommentRequest req) {
        String content = validateContent(req);
        if (poemMapper.countPoemById(poemId) == 0) {
            throw new BusinessException(404, "诗歌不存在或已下架: id=" + poemId);
        }
        Comment comment = new Comment();
        comment.setUserId(userId);
        comment.setPoemId(poemId);
        comment.setContent(content);
        commentMapper.insert(comment);          // 自增主键回填 comment.commentId
        return comment.getCommentId();
    }

    /** 修改自己的评论(管理员也不代改他人评论) */
    public void edit(Long userId, Long commentId, CommentRequest req) {
        String content = validateContent(req);
        Comment comment = requireComment(commentId, userId, null);
        commentMapper.updateContent(comment.getCommentId(), content);
    }

    /** 删除评论: 属主本人, 或管理员 */
    public void delete(Long userId, String role, Long commentId) {
        Comment comment = requireComment(commentId, userId, role);
        commentMapper.deleteComment(comment.getCommentId());
    }

    public PageResult<CommentItem> list(Long poemId, Integer page, Integer pageSize) {
        if (poemMapper.countPoemById(poemId) == 0) {
            throw new BusinessException(404, "诗歌不存在或已下架: id=" + poemId);
        }
        int p = (page == null || page < 1) ? 1 : page;
        int size = (pageSize == null || pageSize < 1) ? 10 : Math.min(pageSize, 50);
        long total = commentMapper.countByPoem(poemId);
        List<CommentItem> list = total == 0
                ? List.of()
                : commentMapper.listByPoem(poemId, (p - 1) * size, size);
        return PageResult.of(total, p, size, list);
    }

    /**
     * 取评论并校验操作权限: 不存在 404; 非属主且非(允许时的)管理员 403。
     * role 传 null 表示不允许管理员越权(如修改他人评论)。
     */
    private Comment requireComment(Long commentId, Long userId, String role) {
        Comment comment = commentMapper.findByCommentId(commentId);
        if (comment == null) {
            throw new BusinessException(404, "评论不存在: id=" + commentId);
        }
        boolean isOwner = comment.getUserId().equals(userId);
        boolean isAdmin = "admin".equals(role);
        if (!isOwner && !isAdmin) {
            throw new BusinessException(403, "只能操作自己的评论");
        }
        return comment;
    }

    private String validateContent(CommentRequest req) {
        String content = req == null || req.getContent() == null ? "" : req.getContent().trim();
        if (content.isEmpty()) {
            throw new IllegalArgumentException("评论内容不能为空");
        }
        if (content.length() > MAX_CONTENT_LENGTH) {
            throw new IllegalArgumentException("评论内容不能超过 " + MAX_CONTENT_LENGTH + " 字");
        }
        return content;
    }
}
