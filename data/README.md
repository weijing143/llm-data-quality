# 数据集说明 · research-feed

从《数据质量研究动态 2025–2026》报告页内嵌数据数组程序化抽取的结构化数据集，
供二次分析与复现。抽取脚本：`analysis/extract_feed.js`，校验脚本：`analysis/validate.py`。

| 文件 | 说明 |
| --- | --- |
| `research-feed.json` | 完整数据集，含 7 个结构化数组（见下） |
| `research-feed.csv` | `FEED` 的扁平表格版：已剥除 HTML 标签、链接以 ` ; ` 连接，带 BOM，Excel / pandas 可直接读取 |

## 顶层结构（JSON）

| 键 | 类型 | 含义 |
| --- | --- | --- |
| `extractedAt` | string | 抽取日期（`YYYY-MM-DD`） |
| `source` | string | 抽取来源文件名 |
| `FEED` | array | 研究动态条目，**主表**，当前 65 条 |
| `LABS` | array | 实验室 / 机构画像，15 条 |
| `TOOLS` | array | 数据工具与基准，12 条 |
| `TRENDS` | array | 趋势判断，6 条 |
| `DEBATES` | array | 开放争论（问题 / 正方 / 反方 / 编者判断），6 条 |
| `DELTA` | array | 相对上一版报告的结论修订记录，7 条 |
| `SOURCES` | array | 信源清单，26 条 |

## FEED 字段口径

| 字段 | 类型 | 含义与约束 |
| --- | --- | --- |
| `date` | string | `YYYY-MM`，事件或发布所在月份 |
| `lab` | string | 单一归属标签：实验室 / 公司 / 机构名；论文以第一作者机构或团队名计，纯学术合作记为 `学界` |
| `topic` | string | 单标签主题，当前枚举：`预训练数据`、`后训练数据`、`去重`、`数据配比`、`合成数据`、`数据治理`、`污染治理`、`数据集`、`开源数据资产`、`工具与基准`、`数据质量定义`（新增主题请先更新本表与 `analysis/validate.py`） |
| `kind` | string | 信源分级：**`官方`** = 论文 / 技术报告 / 官方公告等一手材料；**`二手`** = 媒体或第三方转述分析；**`传闻`** = 未经证实的爆料 |
| `kindLabel` | string | 材料类型的自由标签（如 `论文`、`技术报告`、`模型卡`、`招聘信息`），比 `kind` 更细，不枚举办束 |
| `title` | string | 条目标题 |
| `body` | string | 摘要正文；JSON 版保留 `<b>` 等内嵌 HTML 标签，CSV 版已剥除 |
| `src` | array | 信源链接列表，元素为 `{"t": 链接说明, "u": URL}`；CSV 版合并为分号分隔的纯 URL 串 |

## 其他数组要点

- `LABS`：`name` / `region` / `tone`（页面配色记号）/ `summary` / `points` / `src`
- `TRENDS` 与 `DELTA` 的 `tone`、`DELTA.status`（如 `结论被加强`、`需要改写`）是报告编者的判断标记，非客观字段
- `SOURCES.kind` 与 `FEED.kind` 使用同一套三级分级

## 口径与偏差声明

- 收录范围是**人工策划**的 65 条，不是全量文献计量；存在选择偏差
- 主题与实验室均为**单标签**粗分
- `官方` 仅代表信源性质，不代表内容经过独立复现

## 如何更新

```bash
# 1. 编辑报告页 数据质量研究动态-2025-2026.html 中的 FEED 等数组
# 2. 重新抽取
node analysis/extract_feed.js
# 3. 校验（通过后再提交）
python analysis/validate.py
# 若条目数是有意增加的，更新基线
python analysis/validate.py --update-baseline
# 4. 重新计算统计、图表，并把统计注入 analysis.html
python analysis/analyze.py
```

推送后 GitHub Actions 会自动重跑抽取 + 校验（见 `.github/workflows/validate.yml`）。
