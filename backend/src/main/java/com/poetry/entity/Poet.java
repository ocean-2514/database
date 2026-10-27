package com.poetry.entity;

/**
 * 诗人表 poet 的一行映射, 兼作管理员新增/修改的请求体。
 */
public class Poet {

    private Long poetId;
    private String name;
    private String penName;
    private String gender;       // 男/女, 非法值入库会被 ENUM 拒绝
    private Integer birthYear;
    private Integer deathYear;   // 在世诗人传 null
    private String nationality;
    private String biography;

    public Long getPoetId() {
        return poetId;
    }

    public void setPoetId(Long poetId) {
        this.poetId = poetId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPenName() {
        return penName;
    }

    public void setPenName(String penName) {
        this.penName = penName;
    }

    public String getGender() {
        return gender;
    }

    public void setGender(String gender) {
        this.gender = gender;
    }

    public Integer getBirthYear() {
        return birthYear;
    }

    public void setBirthYear(Integer birthYear) {
        this.birthYear = birthYear;
    }

    public Integer getDeathYear() {
        return deathYear;
    }

    public void setDeathYear(Integer deathYear) {
        this.deathYear = deathYear;
    }

    public String getNationality() {
        return nationality;
    }

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }

    public String getBiography() {
        return biography;
    }

    public void setBiography(String biography) {
        this.biography = biography;
    }
}
