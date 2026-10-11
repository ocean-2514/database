package com.poetry.service;

import com.poetry.common.BusinessException;
import com.poetry.entity.Collection;
import com.poetry.entity.Genre;
import com.poetry.entity.Poem;
import com.poetry.entity.Poet;
import com.poetry.mapper.CollectionMapper;
import com.poetry.mapper.GenreMapper;
import com.poetry.mapper.PoemMapper;
import com.poetry.mapper.PoetMapper;
import org.springframework.dao.DataAccessException;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 管理端业务: 诗人 / 诗歌 / 诗集 / 流派的增删改。
 *
 * 数据库端防线在本层的呈现(答辩演示点):
 *   - 删除有作品的诗人 → 触发器 trg_poet_bd SIGNAL → 转成 400 提示;
 *   - 新增诗歌不写字数 → 触发器 trg_poem_word_count_bi 自动填充;
 *   - 新建诗集调事务存储过程, 部分诗歌ID无效则整体回滚;
 *   - 流派重名 / ISBN 重复 → UNIQUE 约束 → 转成 400 提示。
 */
@Service
public class AdminService {

    private final PoetMapper poetMapper;
    private final PoemMapper poemMapper;
    private final CollectionMapper collectionMapper;
    private final GenreMapper genreMapper;

    public AdminService(PoetMapper poetMapper, PoemMapper poemMapper,
                        CollectionMapper collectionMapper, GenreMapper genreMapper) {
        this.poetMapper = poetMapper;
        this.poemMapper = poemMapper;
        this.collectionMapper = collectionMapper;
        this.genreMapper = genreMapper;
    }

    // ---------------- 诗人 ----------------

    public List<Poet> listPoets() {
        return poetMapper.listAll();
    }

    public long addPoet(Poet poet) {
        if (poet.getName() == null || poet.getName().isBlank()) {
            throw new IllegalArgumentException("诗人姓名不能为空");
        }
        if (poet.getGender() == null || poet.getGender().isBlank()) {
            poet.setGender("男");
        }
        poetMapper.insert(poet);
        return poet.getPoetId();
    }

    public void updatePoet(Long poetId, Poet poet) {
        requirePoet(poetId);
        poet.setPoetId(poetId);
        poetMapper.update(poet);
    }

    public void deletePoet(Long poetId) {
        requirePoet(poetId);
        try {
            poetMapper.deleteById(poetId);
        } catch (DataAccessException e) {
            // 触发器 trg_poet_bd SIGNAL '该诗人名下仍有诗歌作品' 会走到这里
            throw new BusinessException(400, "删除被数据库规则拦截: " + e.getMostSpecificCause().getMessage());
        }
    }

    // ---------------- 诗歌 ----------------

    public long addPoem(Poem poem) {
        validatePoem(poem);
        poemMapper.insertPoem(poem);
        return poem.getPoemId();
    }

    public void updatePoem(Long poemId, Poem poem) {
        validatePoem(poem);
        poem.setPoemId(poemId);
        if (poemMapper.updatePoem(poem) == 0) {
            throw new BusinessException(404, "诗歌不存在: id=" + poemId);
        }
    }

    public void deletePoem(Long poemId) {
        if (poemMapper.deletePoemById(poemId) == 0) {
            throw new BusinessException(404, "诗歌不存在: id=" + poemId);
        }
    }

    private void validatePoem(Poem poem) {
        if (poem.getTitle() == null || poem.getTitle().isBlank()) {
            throw new IllegalArgumentException("诗歌标题不能为空");
        }
        if (poem.getContent() == null || poem.getContent().isBlank()) {
            throw new IllegalArgumentException("诗歌正文不能为空");
        }
        if (poem.getPoetId() == null || poetMapper.countById(poem.getPoetId()) == 0) {
            throw new BusinessException(404, "诗人不存在: id=" + poem.getPoetId());
        }
    }

    // ---------------- 诗集 ----------------

    public List<Collection> listCollections() {
        return collectionMapper.listCatalog();
    }

    public void addCollection(Collection collection) {
        if (collection.getTitle() == null || collection.getTitle().isBlank()) {
            throw new IllegalArgumentException("诗集名称不能为空");
        }
        if (collection.getPoemIds() == null) {
            collection.setPoemIds("");   // 允许先建空诗集
        }
        try {
            collectionMapper.addWithPoems(collection);
        } catch (DataAccessException e) {
            // 存储过程内事务已回滚; 常见原因: poemIds 里有不存在的诗歌ID
            throw new BusinessException(400, "诗集创建失败(已整体回滚): " + e.getMostSpecificCause().getMessage());
        }
    }

    public void updateCollection(Long collectionId, Collection collection) {
        if (collection.getTitle() == null || collection.getTitle().isBlank()) {
            throw new IllegalArgumentException("诗集名称不能为空");
        }
        requireCollection(collectionId);
        collection.setCollectionId(collectionId);
        collectionMapper.update(collection);
    }

    public void deleteCollection(Long collectionId) {
        requireCollection(collectionId);
        collectionMapper.deleteById(collectionId);
    }

    // ---------------- 流派 ----------------

    public void addGenre(Genre genre) {
        if (genre.getName() == null || genre.getName().isBlank()) {
            throw new IllegalArgumentException("流派名称不能为空");
        }
        try {
            genreMapper.insert(genre);
        } catch (DuplicateKeyException e) {
            throw new BusinessException(400, "流派名称已存在");
        }
    }

    public void updateGenre(Long genreId, Genre genre) {
        if (genre.getName() == null || genre.getName().isBlank()) {
            throw new IllegalArgumentException("流派名称不能为空");
        }
        requireGenre(genreId);
        genre.setGenreId(genreId);
        try {
            genreMapper.update(genre);
        } catch (DuplicateKeyException e) {
            throw new BusinessException(400, "流派名称已存在");
        }
    }

    public void deleteGenre(Long genreId) {
        requireGenre(genreId);
        genreMapper.deleteById(genreId);
    }

    // ---------------- 存在性检查 ----------------

    private void requirePoet(Long poetId) {
        if (poetMapper.countById(poetId) == 0) {
            throw new BusinessException(404, "诗人不存在: id=" + poetId);
        }
    }

    private void requireCollection(Long collectionId) {
        if (collectionMapper.countById(collectionId) == 0) {
            throw new BusinessException(404, "诗集不存在: id=" + collectionId);
        }
    }

    private void requireGenre(Long genreId) {
        Genre genre = genreMapper.listGenres().stream()
                .filter(g -> g.getGenreId().equals(genreId))
                .findFirst().orElse(null);
        if (genre == null) {
            throw new BusinessException(404, "流派不存在: id=" + genreId);
        }
    }
}
