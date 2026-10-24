# -*- coding: utf-8 -*-
"""
生成《诗歌信息检索与赏析管理系统》E-R 图的 draw.io 源文件。

用法:
    python gen_er_drawio.py

输出:
    与脚本同目录下的 诗歌系统ER图.drawio，共三页:
      1) 初步E-R图        —— 只含实体与联系
      2) 基本E-R图-诗歌域  —— 诗人 / 诗歌 / 诗集 / 流派 及其属性
      3) 基本E-R图-用户域  —— 用户 / 评分记录 / 评论 / 收藏记录 及其属性
    第二、三页合并即为完整的基本 E-R 图（报告排版时可分别截图）。

记法 (Chen):
    矩形 = 实体, 菱形 = 联系, 椭圆 = 属性, 主键属性加下划线, 1/n/m 标注联系类型。
图内坐标为脚本自动排布的初始值, 打开 https://app.diagrams.net 微调后导出 PNG 即可插入报告。
"""

import os
from xml.sax.saxutils import escape
from xml.dom import minidom

ENT_W, ENT_H = 120, 50
DIA_W, DIA_H = 110, 60
ATTR_W, ATTR_H, ATTR_GAP = 96, 36, 12

ST_ENTITY  = "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
ST_ENTITY2 = "rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
ST_DIAMOND = "rhombus;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;"
ST_ATTR    = "ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;fontSize=11;"
ST_ATTR_PK = "ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=4;fontSize=11;"
ST_ATTR_DERIVED = "ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;dashed=1;fontSize=11;"
ST_TEXT    = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"

POET   = ("poet",  "诗人", [("poet_id", 1), ("姓名", 0), ("笔名", 0), ("性别", 0),
                            ("生年", 0), ("卒年", 0), ("国籍", 0), ("朝代/时期", 0),
                            ("简介", 0), ("创建时间", 0), ("更新时间", 0)])
POEM   = ("poem",  "诗歌", [("poem_id", 1), ("标题", 0), ("正文", 0), ("创作年份", 0),
                            ("体裁", 0), ("字数（派生）", 2), ("赏析", 0), ("发布状态", 0),
                            ("创建时间", 0), ("更新时间", 0)])
POEM_BRIEF = ("poem", "诗歌（属性见图二）", [])   # 用户域页面中的诗歌实体, 不重复画属性
COLL   = ("coll",  "诗集", [("collection_id", 1), ("诗集名称", 0), ("出版年份", 0),
                            ("出版社", 0), ("ISBN", 0), ("简介", 0)])
GENRE  = ("genre", "流派", [("genre_id", 1), ("流派名称", 0), ("描述", 0)])
USER   = ("user",  "用户", [("user_id", 1), ("用户名", 0), ("密码哈希", 0), ("邮箱", 0),
                            ("角色", 0), ("账户状态", 0), ("注册时间", 0)])
RATING = ("rating","评分记录", [("rating_id", 1), ("评分", 0), ("评分时间", 0), ("更新时间", 0)])
COMM   = ("comm",  "评论", [("comment_id", 1), ("评论内容", 0), ("点赞统计值", 0),
                            ("创建时间", 0), ("更新时间", 0)])
FAV    = ("fav",   "收藏记录", [("favorite_id", 1), ("收藏时间", 0), ("收藏类型", 0)])

# 9 个联系: (联系名, 实体A, 实体B, A端基数, B端基数)
RELS = [
    ("创作", POET[0], POEM[0], "1", "n"),
    ("收录", COLL[0], POEM[0], "m", "n"),
    ("属于", POEM[0], GENRE[0], "m", "n"),
    ("评分(用户)", USER[0], RATING[0], "1", "n"),
    ("评分(诗歌)", POEM[0], RATING[0], "1", "n"),
    ("评论(用户)", USER[0], COMM[0], "1", "n"),
    ("评论(诗歌)", POEM[0], COMM[0], "1", "n"),
    ("收藏(用户)", USER[0], FAV[0], "1", "n"),
    ("收藏(诗歌)", POEM[0], FAV[0], "1", "n"),
]

def rect(cells, cid, value, style, x, y, w, h):
    cells.append(
        f'<mxCell id="{cid}" value="{escape(value)}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

def edge(cells, eid, src, tgt, labels=()):
    inner = ['<mxGeometry relative="1" as="geometry"/>']
    for i, (text, pos) in enumerate(labels):
        inner.append(
            f'<mxCell id="{eid}_l{i}" value="{escape(text)}" '
            f'style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];'
            f'labelBackgroundColor=#ffffff;" vertex="1" connectable="0" parent="{eid}">'
            f'<mxGeometry x="{pos}" relative="1" as="geometry"><mxPoint x="4" y="4" as="offset"/>'
            f'</mxGeometry></mxCell>')
    cells.append(
        f'<mxCell id="{eid}" style="edgeStyle=none;html=1;rounded=0;orthogonalLoop=1;jettySize=auto;" '
        f'edge="1" parent="1" source="{src}" target="{tgt}">{"".join(inner)}</mxCell>')

def add_entity(cells, prefix, ent, x, y, style, attr_mode="rows", w=ENT_W, with_attrs=True):
    eid, label, attrs = f"{prefix}_{ent[0]}", ent[1], (ent[2] if with_attrs else [])
    rect(cells, eid, label, style, x, y, w, ENT_H)
    if not attrs:
        return
    n = len(attrs)
    step = ATTR_H + ATTR_GAP
    cy = y + ENT_H / 2 - (n * step - ATTR_GAP) / 2 + ATTR_H / 2
    if attr_mode == "rows":                       # 属性分上下两排
        n_top = (n + 1) // 2
        cx = x + w / 2
        for i, (name, pk) in enumerate(attrs[:n_top]):
            row_w = n_top * ATTR_W + (n_top - 1) * ATTR_GAP
            attr_style = ST_ATTR_PK if pk == 1 else ST_ATTR_DERIVED if pk == 2 else ST_ATTR
            rect(cells, f"{eid}_a{i}", name, attr_style,
                 cx - row_w / 2 + i * (ATTR_W + ATTR_GAP), y - 70, ATTR_W, ATTR_H)
            edge(cells, f"{eid}_ae{i}", eid, f"{eid}_a{i}")
        for j, (name, pk) in enumerate(attrs[n_top:]):
            m = n - n_top
            row_w = m * ATTR_W + (m - 1) * ATTR_GAP
            attr_style = ST_ATTR_PK if pk == 1 else ST_ATTR_DERIVED if pk == 2 else ST_ATTR
            rect(cells, f"{eid}_a{n_top + j}", name, attr_style,
                 cx - row_w / 2 + j * (ATTR_W + ATTR_GAP), y + ENT_H + 34, ATTR_W, ATTR_H)
            edge(cells, f"{eid}_ae{n_top + j}", eid, f"{eid}_a{n_top + j}")
    elif attr_mode == "left":                     # 属性竖排在实体左侧
        ax = x - 60 - ATTR_W
        for i, (name, pk) in enumerate(attrs):
            attr_style = ST_ATTR_PK if pk == 1 else ST_ATTR_DERIVED if pk == 2 else ST_ATTR
            rect(cells, f"{eid}_a{i}", name, attr_style, ax, cy + i * step - ATTR_H / 2, ATTR_W, ATTR_H)
            edge(cells, f"{eid}_ae{i}", eid, f"{eid}_a{i}")
    elif attr_mode == "right":                    # 属性竖排在实体右侧
        ax = x + w + 60
        for i, (name, pk) in enumerate(attrs):
            attr_style = ST_ATTR_PK if pk == 1 else ST_ATTR_DERIVED if pk == 2 else ST_ATTR
            rect(cells, f"{eid}_a{i}", name, attr_style, ax, cy + i * step - ATTR_H / 2, ATTR_W, ATTR_H)
            edge(cells, f"{eid}_ae{i}", eid, f"{eid}_a{i}")

def build_page(name, prefix, entities, rel_coords, style, width, height, legend, with_attrs=True):
    cells = []
    for ent, spec in entities:
        x, y = spec[0], spec[1]
        add_entity(cells, prefix, ent, x, y, style, attr_mode=spec[2] if len(spec) > 2 else "rows",
                   w=spec[3] if len(spec) > 3 else ENT_W, with_attrs=with_attrs)
    for i, (label, a, b, ca, cb) in enumerate(RELS):
        if label not in rel_coords:
            continue
        did = f"{prefix}_d{i}"
        dx, dy = rel_coords[label]
        rect(cells, did, label, ST_DIAMOND, dx, dy, DIA_W, DIA_H)
        edge(cells, f"{prefix}_r{i}a", f"{prefix}_{a}", did, [(ca, -0.75)])
        edge(cells, f"{prefix}_r{i}b", did, f"{prefix}_{b}", [(cb, 0.75)])
    rect(cells, f"{prefix}_legend", legend, ST_TEXT, 60, 20, 760, 24)
    return name, "".join(cells), width, height

def main():
    p1 = build_page(
        "初步E-R图", "p1",
        [(POET, (100, 120)), (POEM, (560, 260)), (COLL, (1020, 120)), (GENRE, (1020, 400)),
         (USER, (100, 560)), (RATING, (420, 560)), (COMM, (760, 620)), (FAV, (1080, 560))],
        {"创作": (330, 180), "收录": (790, 180), "属于": (790, 330),
         "评分(用户)": (250, 570), "评分(诗歌)": (540, 430),
         "评论(用户)": (300, 700), "评论(诗歌)": (700, 470),
         "收藏(用户)": (460, 780), "收藏(诗歌)": (870, 450)},
        ST_ENTITY, 1600, 900,
        "图例：矩形 = 实体　菱形 = 联系　1/n/m = 联系类型（初步E-R图，不含属性）",
        with_attrs=False)

    p2 = build_page(
        "基本E-R图-诗歌域", "p2",
        [(POET, (180, 420, "left")), (POEM, (640, 420)), (COLL, (1140, 420, "right")), (GENRE, (700, 60, "left"))],
        {"创作": (430, 435), "收录": (930, 435), "属于": (820, 210)},
        ST_ENTITY, 1600, 900,
        "图例：矩形 = 实体　菱形 = 联系　椭圆 = 属性　下划线 = 主键　虚线椭圆 = 派生属性（不落表）")

    p3 = build_page(
        "基本E-R图-用户域", "p3",
        [(USER, (160, 380, "left")), (POEM_BRIEF, (560, 380, "rows", 150)),
         (RATING, (1060, 140, "right")), (COMM, (1060, 380, "right")), (FAV, (1060, 620, "right"))],
        {"评分(用户)": (560, 160), "评分(诗歌)": (860, 240),
         "评论(用户)": (420, 560), "评论(诗歌)": (800, 520),
         "收藏(用户)": (400, 700), "收藏(诗歌)": (820, 700)},
        ST_ENTITY2, 1600, 900,
        "图例：矩形 = 实体　菱形 = 联系　椭圆 = 属性　下划线 = 主键　（诗歌属性见图二）")

    diagrams = []
    for i, (name, cells, w, h) in enumerate([p1, p2, p3], 1):
        diagrams.append(
            f'<diagram id="pg{i}" name="{escape(name)}">'
            f'<mxGraphModel dx="1420" dy="820" grid="1" gridSize="10" guides="1" tooltips="1" '
            f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{w}" pageHeight="{h}" '
            f'math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>{cells}'
            f'</root></mxGraphModel></diagram>')
    xml = f'<mxfile host="app.diagrams.net" type="device">{"".join(diagrams)}</mxfile>'

    minidom.parseString(xml)  # 良构性校验
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "诗歌系统ER图.drawio")
    with open(out, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"OK 已生成 {out} (3 页)")

if __name__ == "__main__":
    main()
