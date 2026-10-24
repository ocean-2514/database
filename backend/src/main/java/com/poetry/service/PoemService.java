package com.poetry.service;

import com.poetry.common.PageResult;
import com.poetry.entity.PoemBrief;
import com.poetry.entity.PoemDetail;
import com.poetry.entity.PoemFulltext;
import com.poetry.mapper.PoemMapper;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 诗歌业务逻辑: 组合检索 / 详情 / 全文检索。
 */
@Service
public class PoemService {

    private final PoemMapper poemMapper;

    public PoemService(PoemMapper poemMapper) {
        this.poemMapper = poemMapper;
    }

    /**
     * 组合检索(分页)。
     *
     * @param orderBy 0=最新收录 1=平均分最高 2=标题升序; 其余值按最新收录处理
     */
    public PageResult<PoemBrief> search(String keyword, String poetName, String genre,
                                        Integer yearFrom, Integer yearTo,
                                        Integer orderBy, Integer page, Integer pageSize) {
        int p = (page == null || page < 1) ? 1 : page;
        int size = (pageSize == null || pageSize < 1) ? 10 : Math.min(pageSize, 50);
        int offset = (p - 1) * size;

        long total = poemMapper.countPoems(keyword, poetName, genre, yearFrom, yearTo);
        List<PoemBrief> list = total == 0
                ? List.of()
                : poemMapper.searchPoems(keyword, poetName, genre, yearFrom, yearTo,
                                         orderBy, offset, size);
        return PageResult.of(total, p, size, list);
    }

    public PoemDetail getDetail(Long poemId) {
        PoemDetail detail = poemMapper.getPoemDetail(poemId);
        if (detail == null) {
            throw new IllegalArgumentException("诗歌不存在: id=" + poemId);
        }
        return detail;
    }

    public List<PoemFulltext> fulltextSearch(String keyword) {
        if (keyword == null || keyword.isBlank()) {
            throw new IllegalArgumentException("检索关键词不能为空");
        }
        return poemMapper.searchFulltext(keyword.trim());
    }
}
