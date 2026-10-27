package com.poetry.mapper;

import com.poetry.entity.Comment;
import com.poetry.entity.CommentItem;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 评论数据访问接口, SQL 见 resources/mapper/CommentMapper.xml。
 */
public interface CommentMapper {

    Comment findByCommentId(@Param("commentId") Long commentId);

    /** 某诗的评论列表(分页), 按评论时间倒序 */
    List<CommentItem> listByPoem(@Param("poemId") Long poemId,
                                 @Param("offset") int offset,
                                 @Param("pageSize") int pageSize);

    long countByPoem(@Param("poemId") Long poemId);

    /** 新增评论, useGeneratedKeys 回填自增主键到 comment.commentId */
    int insert(Comment comment);

    int updateContent(@Param("commentId") Long commentId, @Param("content") String content);

    int deleteComment(@Param("commentId") Long commentId);
}
