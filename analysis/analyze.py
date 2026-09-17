# -*- coding: utf-8 -*-
"""数据质量 × 大模型 · 研究动态数据分析
读取 data/research-feed.json，产出统计数字（analysis/stats.json）与图表（analysis/charts/*.png）
用法: python analysis/analyze.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "research-feed.json"
CHARTS = ROOT / "analysis" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

feed = json.loads(DATA.read_text(encoding="utf-8"))["FEED"]
print(f"载入条目: {len(feed)}")

months = sorted(x["date"] for x in feed if x.get("date"))
labs = Counter(x["lab"] for x in feed)
topics = Counter(x["topic"] for x in feed)
kinds = Counter(x["kind"] for x in feed)
by_month = Counter(months)

stats = {
    "total_items": len(feed),
    "lab_count": len(labs),
    "topic_count": len(topics),
    "span": f"{months[0]} ~ {months[-1]}",
    "by_lab": dict(labs.most_common()),
    "by_topic": dict(topics.most_common()),
    "by_kind": dict(kinds),
    "by_month": {k: by_month[k] for k in sorted(by_month)},
    "official_ratio": round(kinds.get("官方", 0) / len(feed) * 100, 1),
    "top_lab": labs.most_common(1)[0][0],
    "top_lab_n": labs.most_common(1)[0][1],
    "top_topic": topics.most_common(1)[0][0],
    "top_topic_n": topics.most_common(1)[0][1],
}
(ROOT / "analysis" / "stats.json").write_text(
    json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from daimon_runtime import setup_plot
setup_plot()

# 与项目页面一致的深色调色板
BG = "#0b0e16"
FG = "#ffffffd9"
SUB = "#ffffff73"
SIG, CY, IND, AMB, DAN = "#4ADE9B", "#22D3EE", "#818CF8", "#FBBF24", "#FB7185"
GRID = "#ffffff14"


def style_ax(ax, title):
    ax.set_facecolor(BG)
    ax.set_title(title, color=FG, fontsize=13, fontweight="bold", loc="left", pad=12)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=SUB, labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def new_fig(w=8.2, h=3.6):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    return fig, ax


# 1) 月度条目时间线
fig, ax = new_fig()
ms = sorted(by_month)
ax.bar(range(len(ms)), [by_month[m] for m in ms], color=SIG, width=0.62)
ax.set_xticks(range(len(ms)))
ax.set_xticklabels(ms, rotation=45, ha="right")
for i, m in enumerate(ms):
    ax.text(i, by_month[m] + 0.15, str(by_month[m]), ha="center", color=FG, fontsize=8.5)
style_ax(ax, "收录条目按月份分布")
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.grid(axis="x", visible=False)
fig.savefig(CHARTS / "by_month.png", bbox_inches="tight", facecolor=BG, dpi=150)
plt.close(fig)

# 2) 实验室分布（Top 10）
fig, ax = new_fig(h=4.2)
top = labs.most_common(10)
names = [k for k, _ in top][::-1]
vals = [v for _, v in top][::-1]
colors = [SIG if n == stats["top_lab"] else IND for n in names]
ax.barh(names, vals, color=colors, height=0.58)
for i, v in enumerate(vals):
    ax.text(v + 0.15, i, str(v), va="center", color=FG, fontsize=9)
style_ax(ax, "条目按实验室 / 团队分布（Top 10）")
ax.grid(axis="x", color=GRID, linewidth=0.8)
ax.grid(axis="y", visible=False)
fig.savefig(CHARTS / "by_lab.png", bbox_inches="tight", facecolor=BG, dpi=150)
plt.close(fig)

# 3) 主题分布
fig, ax = new_fig(h=3.8)
tt = topics.most_common()
names = [k for k, _ in tt][::-1]
vals = [v for _, v in tt][::-1]
ax.barh(names, vals, color=CY, height=0.58)
for i, v in enumerate(vals):
    ax.text(v + 0.12, i, str(v), va="center", color=FG, fontsize=9)
style_ax(ax, "条目按研究主题分布")
ax.grid(axis="x", color=GRID, linewidth=0.8)
ax.grid(axis="y", visible=False)
fig.savefig(CHARTS / "by_topic.png", bbox_inches="tight", facecolor=BG, dpi=150)
plt.close(fig)

# 4) 信源可信度构成
fig, ax = plt.subplots(figsize=(4.6, 3.6), facecolor=BG)
ax.set_facecolor(BG)
order = ["官方", "二手", "传闻"]
vals = [kinds.get(k, 0) for k in order]
cols = [SIG, AMB, DAN]
wedges, texts, autotexts = ax.pie(
    vals, labels=order, colors=cols, autopct="%1.0f%%", startangle=90,
    textprops={"color": FG, "fontsize": 11}, pctdistance=0.72,
    wedgeprops={"width": 0.42, "edgecolor": BG, "linewidth": 2},
)
for t in autotexts:
    t.set_color("#0b0e16"); t.set_fontweight("bold"); t.set_fontsize(10)
ax.text(0, 0, f"{stats['official_ratio']}%\n官方", ha="center", va="center",
        color=FG, fontsize=13, fontweight="bold")
ax.set_title("信源类型构成", color=FG, fontsize=13, fontweight="bold", loc="left", pad=12)
fig.savefig(CHARTS / "by_kind.png", bbox_inches="tight", facecolor=BG, dpi=150)
plt.close(fig)

print(json.dumps(stats, ensure_ascii=False, indent=2))
print("图表输出: analysis/charts/{by_month,by_lab,by_topic,by_kind}.png")
