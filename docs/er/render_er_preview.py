# -*- coding: utf-8 -*-
"""Render the generated draw.io pages to a single review PNG.

Run from any directory with Python and matplotlib installed:
    python render_er_preview.py
"""
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, Rectangle
from matplotlib.font_manager import FontProperties

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "诗歌系统ER图.drawio"
OUTPUT = HERE / "_layout_preview.png"

font_candidates = [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
]
font_file = next((path for path in font_candidates if path.exists()), None)
font = FontProperties(fname=str(font_file), size=8) if font_file else FontProperties(size=8)
small_font = FontProperties(fname=str(font_file), size=7) if font_file else FontProperties(size=7)
cardinality_font = FontProperties(fname=str(font_file), size=10, weight="bold") if font_file else FontProperties(size=10, weight="bold")


def boundary_radius(cell, width, height, ux, uy):
    """Distance from a node center to its outline along a unit vector."""
    style = cell.get("style", "")
    half_w, half_h = width / 2, height / 2
    if "rhombus" in style:
        denom = abs(ux) / half_w + abs(uy) / half_h
        return 1 / denom if denom else 0
    if "ellipse" in style:
        denom = (ux / half_w) ** 2 + (uy / half_h) ** 2
        return (1 / denom ** 0.5) if denom else 0
    candidates = []
    if abs(ux) > 1e-9:
        candidates.append(half_w / abs(ux))
    if abs(uy) > 1e-9:
        candidates.append(half_h / abs(uy))
    return min(candidates) if candidates else 0


def render_page(ax, diagram):
    model = diagram.find("./mxGraphModel/root")
    cells = list(model.findall("mxCell"))
    vertices = {}
    edges = []
    pending_labels = []
    for cell in cells:
        if cell.get("vertex") == "1":
            geom = cell.find("mxGeometry")
            if geom is None or geom.get("x") is None:
                continue
            x, y = float(geom.get("x")), float(geom.get("y"))
            w, h = float(geom.get("width")), float(geom.get("height"))
            vertices[cell.get("id")] = (cell, x, y, w, h)
        elif cell.get("edge") == "1":
            edges.append(cell)

    for edge in edges:
        source = vertices.get(edge.get("source"))
        target = vertices.get(edge.get("target"))
        if not source or not target:
            continue
        _, x1, y1, w1, h1 = source
        _, x2, y2, w2, h2 = target
        ax.plot([x1 + w1 / 2, x2 + w2 / 2], [y1 + h1 / 2, y2 + h2 / 2],
                color="#999999", linewidth=0.8, zorder=1)
        distance = ((x2 + w2 / 2 - x1 - w1 / 2) ** 2 +
                    (y2 + h2 / 2 - y1 - h1 / 2) ** 2) ** 0.5
        if distance:
            ux = (x2 + w2 / 2 - x1 - w1 / 2) / distance
            uy = (y2 + h2 / 2 - y1 - h1 / 2) / distance
            r_source = boundary_radius(source[0], w1, h1, ux, uy)
            r_target = boundary_radius(target[0], w2, h2, ux, uy)
            for child in edge.findall("mxCell"):
                label = child.get("value", "")
                if not label:
                    continue
                geom = child.find("mxGeometry")
                side = float(geom.get("x", "0")) if geom is not None else 0
                gap = 16
                if side < 0:
                    along = min(max(r_source + gap, distance * 0.28), distance * 0.46)
                else:
                    along = max(min(distance - r_target - gap, distance * 0.72), distance * 0.54)
                pending_labels.append((x1 + w1 / 2 + ux * along,
                                       y1 + h1 / 2 + uy * along,
                                       label, 1 if side < 0 else -1))

    for cell, x, y, w, h in vertices.values():
        style = cell.get("style", "")
        label = cell.get("value", "")
        cx, cy = x + w / 2, y + h / 2
        if "rhombus" in style:
            patch = Polygon([(cx, y), (x + w, cy), (cx, y + h), (x, cy)],
                            closed=True, facecolor="#ffe6cc", edgecolor="#d79b00", linewidth=1.0, zorder=3)
        elif "ellipse" in style:
            dashed = "dashed=1" in style
            fill = "#fff2cc" if "#fff2cc" in style else "white"
            edgecolor = "#d6b656" if fill == "#fff2cc" else "#999999"
            patch = Ellipse((cx, cy), w, h, facecolor=fill, edgecolor=edgecolor,
                            linewidth=0.9, linestyle="--" if dashed else "-", zorder=3)
        elif "strokeColor=none" in style:
            ax.text(x, cy, label, fontproperties=small_font, va="center", ha="left", zorder=4)
            continue
        else:
            fill = "#d5e8d4" if "#d5e8d4" in style else "#dae8fc"
            edgecolor = "#82b366" if fill == "#d5e8d4" else "#6c8ebf"
            patch = Rectangle((x, y), w, h, facecolor=fill, edgecolor=edgecolor,
                              linewidth=1.0, zorder=3)
        ax.add_patch(patch)
        ax.text(cx, cy, label, fontproperties=small_font, ha="center", va="center", zorder=4)

    # Draw relationship cardinalities last so node fills cannot cover them.
    for lx, ly, label, side in pending_labels:
        ax.text(lx, ly + side * 9, label, color="#a00018", ha="center", va="center",
                fontproperties=cardinality_font, zorder=10,
                bbox={"facecolor": "white", "edgecolor": "#aaaaaa", "linewidth": 0.45,
                      "boxstyle": "round,pad=0.16"})

    ax.set_xlim(0, 1600)
    ax.set_ylim(900, 0)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.set_title(diagram.get("name", "E-R 图"), fontproperties=font, pad=4)


def main():
    root = ET.parse(SOURCE).getroot()
    diagrams = root.findall("diagram")
    fig, axes = plt.subplots(len(diagrams), 1, figsize=(16, 9 * len(diagrams)), dpi=100)
    if len(diagrams) == 1:
        axes = [axes]
    for ax, diagram in zip(axes, diagrams):
        render_page(ax, diagram)
    fig.subplots_adjust(hspace=0.06, top=0.99, bottom=0.01, left=0.01, right=0.99)
    fig.savefig(OUTPUT, dpi=100, facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
