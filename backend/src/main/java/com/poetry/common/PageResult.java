package com.poetry.common;

import java.util.List;

/**
 * 分页结果: 与存储过程 sp_search_poems 的两个结果集语义一致,
 * 这里由 Service 层用 COUNT + LIMIT 两条 SQL 组装。
 */
public class PageResult<T> {

    private long total;      // 满足条件的总条数
    private int page;        // 当前页码, 从 1 开始
    private int pageSize;    // 每页条数
    private List<T> list;    // 当前页数据

    public PageResult() {
    }

    public PageResult(long total, int page, int pageSize, List<T> list) {
        this.total = total;
        this.page = page;
        this.pageSize = pageSize;
        this.list = list;
    }

    public static <T> PageResult<T> of(long total, int page, int pageSize, List<T> list) {
        return new PageResult<>(total, page, pageSize, list);
    }

    public long getTotal() {
        return total;
    }

    public void setTotal(long total) {
        this.total = total;
    }

    public int getPage() {
        return page;
    }

    public void setPage(int page) {
        this.page = page;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }

    public List<T> getList() {
        return list;
    }

    public void setList(List<T> list) {
        this.list = list;
    }
}
