package com.poetry.mapper;

import com.poetry.entity.Collection;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 诗集数据访问接口(管理端), SQL 见 resources/mapper/CollectionMapper.xml。
 */
public interface CollectionMapper {

    /** 目录列表: 查视图 v_collection_catalog(含 poem_count) */
    List<Collection> listCatalog();

    long countById(@Param("collectionId") Long collectionId);

    /** 新增诗集并批量收录诗歌: 调用事务存储过程 sp_add_collection_with_poems */
    int addWithPoems(Collection collection);

    int update(Collection collection);

    int deleteById(@Param("collectionId") Long collectionId);
}
