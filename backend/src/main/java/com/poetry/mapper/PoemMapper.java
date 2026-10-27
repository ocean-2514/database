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

    /** 组合检索(分页): 条件全部可空, 由 XML 中 &lt;if&gt; 动态拼接; 只检索已发布诗歌 */
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

    /** 诗歌详情: 查询视图 v_poem_detail(视图内只含已发布诗歌) */
    PoemDetail getPoemDetail(@Param("poemId") Long poemId);

    /** 已发布诗歌的存在性检查(收藏/评分/评论等互动操作前置校验用) */
    long countPoemById(@Param("poemId") Long poemId);

    /** 中文全文检索: 调用存储过程 sp_fulltext_search_poems (statementType=CALLABLE) */
    List<PoemFulltext> searchFulltext(@Param("keyword") String keyword);

    /** 管理端: 新增诗歌(字数不落表, 查询时派生), 回填自增主键 */
    int insertPoem(com.poetry.entity.Poem poem);

    /** 管理端: 修改诗歌 */
    int updatePoem(com.poetry.entity.Poem poem);

    /** 管理端: 变更发布状态(published/withdrawn) */
    int updatePublicationStatus(@Param("poemId") Long poemId, @Param("status") String status);

    /** 管理端: 物理删除(有关联互动记录时会被 RESTRICT 外键拦截) */
    int deletePoemById(@Param("poemId") Long poemId);
}
