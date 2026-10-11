package com.poetry.mapper;

import com.poetry.entity.PoemBrief;
import com.poetry.entity.PoemDetail;
import com.poetry.entity.PoemFulltext;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 诗歌数据访问接口。
 * SQL 实现在 resources/mapper/PoemMapper.xml, 全部为手写原生 SQL。
 */
public interface PoemMapper {

    /** 组合检索(分页): 条件全部可空, 由 XML 中 &lt;if&gt; 动态拼接 */
    List<PoemBrief> searchPoems(@Param("keyword") String keyword,
                                @Param("poetName") String poetName,
                                @Param("genre") String genre,
                                @Param("yearFrom") Integer yearFrom,
                                @Param("yearTo") Integer yearTo,
                                @Param("orderBy") Integer orderBy,
                                @Param("offset") int offset,
                                @Param("pageSize") int pageSize);

    /** 组合检索(总数): 与 searchPoems 共用 &lt;sql&gt; 条件片段 */
    long countPoems(@Param("keyword") String keyword,
                    @Param("poetName") String poetName,
                    @Param("genre") String genre,
                    @Param("yearFrom") Integer yearFrom,
                    @Param("yearTo") Integer yearTo);

    /** 诗歌详情: 查询视图 v_poem_detail */
    PoemDetail getPoemDetail(@Param("poemId") Long poemId);

    /** 中文全文检索: 调用存储过程 sp_fulltext_search_poems (statementType=CALLABLE) */
    List<PoemFulltext> searchFulltext(@Param("keyword") String keyword);
}
