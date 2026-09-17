# -*- coding: utf-8 -*-
"""数据质量 × 大模型 · 数据集校验
对 data/research-feed.json / .csv 做结构与口径检查，供本地与 CI 使用。
用法:
    python analysis/validate.py                  # 校验，出错时退出码 1
    python analysis/validate.py --update-baseline  # 条目数有意增加后更新基线
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "research-feed.json"
CSV = ROOT / "data" / "research-feed.csv"
BASELINE = ROOT / "analysis" / "baseline.json"

KINDS = {"官方", "二手", "传闻"}
TOPICS = {
    "预训练数据", "后训练数据", "去重", "数据配比", "合成数据", "数据治理",
    "污染治理", "数据集", "开源数据资产", "工具与基准", "数据质量定义",
}
FEED_KEYS = {"date", "lab", "topic", "kind", "kindLabel", "title", "body", "src"}
SCHEMA = {
    "LABS": {"name", "region", "tone", "summary", "points", "src"},
    "TOOLS": {"name", "type", "org", "what", "src"},
    "TRENDS": {"kicker", "tone", "title", "body", "evidence", "src"},
    "DEBATES": {"q", "a", "b", "judge"},
    "DELTA": {"status", "tone", "title", "body"},
    "SOURCES": {"kind", "t", "u", "note"},
}
DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def check_links(src, where):
    if not isinstance(src, list) or not src:
        err(f"{where}: src 为空或不是列表")
        return
    for i, link in enumerate(src):
        if not isinstance(link, dict) or not str(link.get("u", "")).startswith("http"):
            err(f"{where}: 第 {i + 1} 个信源缺少有效 URL")


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))

    # ── 顶层结构 ────────────────────────────────
    for key in ["extractedAt", "source", "FEED", *SCHEMA]:
        if key not in d:
            err(f"顶层缺少键 {key}")
            return finish()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", d["extractedAt"]):
        err(f"extractedAt 日期格式非法: {d['extractedAt']}")

    # ── FEED 主表 ───────────────────────────────
    feed = d["FEED"]
    seen_titles = set()
    for i, x in enumerate(feed):
        where = f"FEED[{i}]《{str(x.get('title', '?'))[:20]}》"
        missing = FEED_KEYS - x.keys()
        if missing:
            err(f"{where}: 缺字段 {sorted(missing)}")
            continue
        if not DATE_RE.match(x["date"]):
            err(f"{where}: date 格式非法: {x['date']!r}（应为 YYYY-MM）")
        if x["kind"] not in KINDS:
            err(f"{where}: kind 非法: {x['kind']!r}（应为 {'/'.join(sorted(KINDS))}）")
        if x["topic"] not in TOPICS:
            warn(f"{where}: 新主题 {x['topic']!r}，请确认后同步 data/README.md 与 validate.py 的 TOPICS")
        for f in ("lab", "title", "body", "kindLabel"):
            if not str(x[f]).strip():
                err(f"{where}: {f} 为空")
        check_links(x["src"], where)
        if x["title"] in seen_titles:
            err(f"{where}: 标题重复")
        seen_titles.add(x["title"])

    # ── 附属数组结构 ─────────────────────────────
    for name, keys in SCHEMA.items():
        arr = d[name]
        if not arr:
            err(f"{name} 为空")
            continue
        for i, x in enumerate(arr):
            if not isinstance(x, dict) or keys - x.keys():
                err(f"{name}[{i}]: 缺字段 {sorted(keys - x.keys())}")
            if name == "SOURCES":
                if not str(x.get("u", "")).startswith("http"):
                    err(f"SOURCES[{i}]: URL 非法")
                if x.get("kind") not in KINDS:
                    err(f"SOURCES[{i}]: kind 非法: {x.get('kind')!r}")

    # ── CSV 一致性 ──────────────────────────────
    with CSV.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != len(feed):
        err(f"CSV 行数（{len(rows)}）与 FEED 条数（{len(feed)}）不一致，请重跑 extract_feed.js")

    # ── 条数基线（单调不减） ──────────────────────
    counts = {"FEED": len(feed), **{k: len(d[k]) for k in SCHEMA}}
    if "--update-baseline" in sys.argv:
        BASELINE.write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"基线已更新: {counts}")
    elif BASELINE.exists():
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        for k, n in counts.items():
            if n < base.get(k, 0):
                err(f"{k} 条数 {n} 低于基线 {base[k]}——若非有意删减，请检查报告页改动")
    else:
        warn("未找到 baseline.json，跳过条数基线检查（可用 --update-baseline 创建）")

    finish(counts)


def finish(counts=None):
    for w in warnings:
        print(f"⚠ 警告: {w}")
    if errors:
        for e in errors:
            print(f"✗ 错误: {e}")
        print(f"\n校验失败：{len(errors)} 个错误，{len(warnings)} 个警告")
        sys.exit(1)
    print(f"✓ 校验通过（{counts['FEED'] if counts else '?'} 条 FEED，{len(warnings)} 个警告）")


if __name__ == "__main__":
    main()
