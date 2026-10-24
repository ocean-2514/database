package com.poetry.mapper;

import com.poetry.dto.RegisterParam;
import com.poetry.entity.User;
import org.apache.ibatis.annotations.Param;

/**
 * 用户数据访问接口, SQL 见 resources/mapper/UserMapper.xml。
 */
public interface UserMapper {

    User findByUsername(@Param("username") String username);

    User findByUserId(@Param("userId") Long userId);

    /** 注册: 调用存储过程 sp_register_user, OUT 参数回填到 param.userId */
    void register(RegisterParam param);
}
