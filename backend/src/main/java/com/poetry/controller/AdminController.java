package com.poetry.controller;

import com.poetry.annotation.RequireAdmin;
import com.poetry.common.ApiResponse;
import com.poetry.entity.Collection;
import com.poetry.entity.Genre;
import com.poetry.entity.Poem;
import com.poetry.entity.Poet;
import com.poetry.service.AdminService;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * 管理端接口(全部 @RequireAdmin: 未登录 401, 非管理员 403)。
 * 覆盖诗人 / 诗歌 / 诗集 / 流派 的增删改与列表。
 */
@RestController
@RequireAdmin
public class AdminController {

    private final AdminService adminService;

    public AdminController(AdminService adminService) {
        this.adminService = adminService;
    }

    // ---------------- 诗人 ----------------

    @GetMapping("/api/admin/poets")
    public ApiResponse<List<Poet>> listPoets() {
        return ApiResponse.ok(adminService.listPoets());
    }

    /** POST /api/admin/poets, 请求体 JSON(name 必填) */
    @PostMapping("/api/admin/poets")
    public ApiResponse<Map<String, Long>> addPoet(@RequestBody Poet poet) {
        return ApiResponse.ok(Map.of("poetId", adminService.addPoet(poet)));
    }

    @PutMapping("/api/admin/poets/{poetId}")
    public ApiResponse<Void> updatePoet(@PathVariable Long poetId, @RequestBody Poet poet) {
        adminService.updatePoet(poetId, poet);
        return ApiResponse.ok(null);
    }

    @DeleteMapping("/api/admin/poets/{poetId}")
    public ApiResponse<Void> deletePoet(@PathVariable Long poetId) {
        adminService.deletePoet(poetId);
        return ApiResponse.ok(null);
    }

    // ---------------- 诗歌 ----------------

    /** POST /api/admin/poems, 请求体 JSON(title/content/poetId 必填, 字数自动维护) */
    @PostMapping("/api/admin/poems")
    public ApiResponse<Map<String, Long>> addPoem(@RequestBody Poem poem) {
        return ApiResponse.ok(Map.of("poemId", adminService.addPoem(poem)));
    }

    @PutMapping("/api/admin/poems/{poemId}")
    public ApiResponse<Void> updatePoem(@PathVariable Long poemId, @RequestBody Poem poem) {
        adminService.updatePoem(poemId, poem);
        return ApiResponse.ok(null);
    }

    /** DELETE /api/admin/poems/{id} —— 下架, 互动数据级联清除 */
    @DeleteMapping("/api/admin/poems/{poemId}")
    public ApiResponse<Void> deletePoem(@PathVariable Long poemId) {
        adminService.deletePoem(poemId);
        return ApiResponse.ok(null);
    }

    // ---------------- 诗集 ----------------

    @GetMapping("/api/admin/collections")
    public ApiResponse<List<Collection>> listCollections() {
        return ApiResponse.ok(adminService.listCollections());
    }

    /** POST /api/admin/collections, poemIds 传逗号分隔的诗歌ID串(可空), 存储过程事务写入 */
    @PostMapping("/api/admin/collections")
    public ApiResponse<Void> addCollection(@RequestBody Collection collection) {
        adminService.addCollection(collection);
        return ApiResponse.ok(null);
    }

    @PutMapping("/api/admin/collections/{collectionId}")
    public ApiResponse<Void> updateCollection(@PathVariable Long collectionId,
                                              @RequestBody Collection collection) {
        adminService.updateCollection(collectionId, collection);
        return ApiResponse.ok(null);
    }

    @DeleteMapping("/api/admin/collections/{collectionId}")
    public ApiResponse<Void> deleteCollection(@PathVariable Long collectionId) {
        adminService.deleteCollection(collectionId);
        return ApiResponse.ok(null);
    }

    // ---------------- 流派 ----------------

    @PostMapping("/api/admin/genres")
    public ApiResponse<Map<String, Long>> addGenre(@RequestBody Genre genre) {
        adminService.addGenre(genre);
        return ApiResponse.ok(Map.of("genreId", genre.getGenreId() == null ? 0L : genre.getGenreId()));
    }

    @PutMapping("/api/admin/genres/{genreId}")
    public ApiResponse<Void> updateGenre(@PathVariable Long genreId, @RequestBody Genre genre) {
        adminService.updateGenre(genreId, genre);
        return ApiResponse.ok(null);
    }

    @DeleteMapping("/api/admin/genres/{genreId}")
    public ApiResponse<Void> deleteGenre(@PathVariable Long genreId) {
        adminService.deleteGenre(genreId);
        return ApiResponse.ok(null);
    }
}
