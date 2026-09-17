# 数据质量 × 大模型 · 学习分析项目

围绕「数据质量对大模型的价值」这一主题的学习分析项目：三份互相衔接的单页报告 + 一个结构化数据集 + 可复现的定量分析 + 一条四阶段学习路径。所有页面均为**单文件静态 HTML、无外部请求**，可离线直接打开，也可部署到 GitHub Pages。

> 数据截至 2026-09-16。市场预测类数据口径各异，仅供参考，不构成投资建议。

## 在线阅读

部署 GitHub Pages 后，入口为 `index.html`。

## 项目结构

```
llm-data-quality/
│
├── index.html                          ← 门户：项目导航、数据概览、推荐阅读顺序
├── analysis.html                       ← 分析层：数据集的定量画像（数字由 analyze.py 动态注入）
├── learning.html                       ← 学习路径：四阶段课程（localStorage 进度记录）
│
├── 数据质量优化对大模型价值.html        ← 报告 · 框架篇：机制 / 工程 / 投入产出 【来源：页脚 32 篇文献】
├── 数据质量研究动态-2025-2026.html      ← 报告 · 动态篇：各实验室追踪 【数据集唯一来源；页脚 43 篇文献】
├── 数据质量近6个月汇总-2026-09.html     ← 报告 · 汇总篇：论文 / 政策 / 市场 【来源：页脚 7 篇 + 政策文号 + 市场报告】
│
├── data/                               ← 数据层
│   ├── research-feed.json              · 结构化数据集（FEED 65 条 + 6 个附属数组，含 26 条信源清单）
│   ├── research-feed.csv               · FEED 的扁平表格版（Excel / pandas 直读）
│   └── README.md                       · Schema 文档：字段口径、枚举值、偏差声明、更新方法
│
├── analysis/                           ← 分析层（可复现）
│   ├── extract_feed.js                 · Node 脚本：从动态篇 HTML 抽取数据集
│   ├── analyze.py                      · 统计 + 4 张图表 + 把统计注入 analysis.html
│   ├── validate.py                     · 校验：日期 / 枚举 / 链接 / 条数单调不减
│   ├── stats.json                      · 统计结果（analyze.py 生成）
│   ├── baseline.json                   · 条数基线（validate.py 对照）
│   └── charts/                         · by_month / by_lab / by_topic / by_kind 四张图
│
├── assets/
│   └── cover.png                       ← 分享封面（OG 卡片图，1200×630）
│
├── .github/workflows/validate.yml      ← CI：push 时自动重抽取 + 一致性比对 + 校验
│
└── README.md                           ← 本文件
```

数据主线：**动态篇 HTML 是原始语料** → `extract_feed.js` 抽成 `data/` 数据集 → `analyze.py` 算出统计图表并注入 `analysis.html` → `validate.py` + GitHub Actions 保证链路不失真。

## 信息来源

本项目所有关键数字与论断都可溯源，按三层组织：

**① 报告页脚。** 三份报告各自在页脚给出完整出处（论文 arXiv 编号、政策文号、市场报告口径），并区分一手来源、二手转述与传闻；三份报告的引用集合**互不重叠**（32 / 43 / 7 篇）。

**② 数据集信源清单。** `data/research-feed.json` 的 `SOURCES` 数组收录 26 条核心信源（官方 24 / 二手 2），FEED 每条动态的 `src` 字段附原文链接。核心条目一览：

<details>
<summary><b>官方一手信源（24 条）</b></summary>

- DeepSeek-V4（[arXiv:2606.19348](https://arxiv.org/abs/2606.19348)）— >32T token、§4.1 数据构建、移除模板化网页防崩溃
- DeepSeek-V4.1-Flash 模型卡（[HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)）— 从零 45T 多模态 token，「所有实质变化都在数据管线」
- DeepSeek-V3.2（[arXiv:2512.02556](https://arxiv.org/abs/2512.02556)）— 1,827 环境 / 8.5 万 prompt 的智能体任务合成管线
- DeepSeekMath-V2（[arXiv:2511.22570](https://arxiv.org/abs/2511.22570)）— 全自动标注取代人工，验证器质量 0.85→0.96
- DeepSeek 预训练数据团队招聘页（[猎聘](https://www.liepin.com/job/1985042903.shtml)）— 官方首次点名 MinHash 去重与向量去重
- Apple · DataComp-VLM（[arXiv:2606.28551](https://arxiv.org/abs/2606.28551)）— 「data mixing, not filtering, is key」
- Apple · 数据质量幻觉（[arXiv:2510.00866](https://arxiv.org/abs/2510.00866)）— 质量指标提升下游却未必改善语言建模
- Apple · 数据受限混合律（[arXiv:2605.12715](https://arxiv.org/abs/2605.12715)）— 稀缺语料可复用 15–20 次
- Apple · 重复训练与去重（[arXiv:2503.07879](https://arxiv.org/abs/2503.07879)）— 10 epoch 胜 10 倍大数据集
- NVIDIA · Nemotron-CC v2（[arXiv:2412.02595v2](https://arxiv.org/html/2412.02595v2)）— 高质 token 占比 9%→25%
- Ai2 · Dolma 3 / Olmo 3（[allenai.org](https://allenai.org/blog/olmo3)）— 5.93T 配方全公开
- HuggingFace · FineWeb2（[arXiv:2506.20920](https://arxiv.org/abs/2506.20920)）— 20TB / 1000+ 语言
- Google · Gemini 3 Pro 模型卡（[PDF](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf)）— 六类数据来源 + 去重
- Google · Gemma 3（[arXiv:2503.19786](https://arxiv.org/abs/2503.19786)）— 27B/14T、12B/12T 等配比比率
- Microsoft · Phi-4-mini-flash-reasoning（[arXiv:2507.06607](https://arxiv.org/abs/2507.06607)）— 全合成数学数据
- DataEvolve · 演化式数据策展（[arXiv:2603.14420](https://arxiv.org/html/2603.14420v1)）— Darwin-CC 504B，token −25%
- 污染检测脆弱性（[ICLR 2026, arXiv:2510.02386](https://arxiv.org/abs/2510.02386)）— 短暂 GRPO 即可掩盖检测信号
- GEM 2026 污染检测综述（[ACL Anthology](https://aclanthology.org/2026.gem-main.50/)）— 55 项研究：虚高 6%–40%
- 过度过滤审计（[arXiv:2606.05936](https://arxiv.org/abs/2606.05936)）— 人工会保留 88.5% 被过滤内容
- 字节 Seed-Coder 数据管线（[arXiv:2506.03524](https://arxiv.org/abs/2506.03524)）— 数据削减约 98%
- 面壁智能 · UltraData L0–L4（[arXiv:2602.09003](https://arxiv.org/abs/2602.09003)）— 五层数据管理框架
- 月之暗面 · Kimi K2 改写提效（[arXiv:2507.20534](https://arxiv.org/html/2507.20534v1)）— SimpleQA 23.76 → 28.94
- 智谱 · GLM-5（[arXiv:2602.15763](https://arxiv.org/html/2602.15763v1)）— 28.5T；去重后唯一 token +28%
- 工具链版本页（[datatrove / NeMo Curator / Data-Juicer / text-dedup](https://pypi.org/project/datatrove/)）— 版本与能力变更

</details>

<details>
<summary><b>二手信源（2 条，事实待独立验证）</b></summary>

- 美国 CISA/FBI/NSA 蒸馏指控与中方回应（[Piracy Monitor](https://piracymonitor.org/us-warns-of-industrial-scale-distillation-against-us-ai-platforms-by-china-based-ai-companies/)，2026-09）
- EU AI Act GPAI 透明度义务（[artificialintelligenceact.eu](https://artificialintelligenceact.eu/)，2025-08-02 生效）

</details>

**③ 分析层数字。** `analysis.html` 中所有统计数字由 `analysis/analyze.py` 从数据集计算并注入，重跑脚本即可复现；口径与局限见该页「方法」一节及 `data/README.md` 的偏差声明。

## 推荐阅读顺序

1. **框架篇** — 建立「质量 = 单位 token 的有效梯度」的心智模型
2. **动态篇** — 把框架对照各实验室的真实做法
3. **分析层** — 把 65 条动态当成数据集，看热度、结构与信源
4. **汇总篇** — 看最新论文争议、政策与产业走向

想按课程节奏系统学习（约 2–3 周），直接打开 `learning.html`。

## 复现分析

```bash
cd llm-data-quality

# 1. 从动态篇 HTML 重新抽取数据集（需要 Node.js）
node analysis/extract_feed.js

# 2. 校验数据集（口径 / 格式 / 条数基线）
python analysis/validate.py

# 3. 重新计算统计并生成图表（需要 Python + matplotlib + pandas）
python analysis/analyze.py
```

每次 push 时 GitHub Actions 会自动重跑抽取与校验（`.github/workflows/validate.yml`）。

## 本地查看

直接双击任意 `.html` 文件即可；或启动一个本地服务：

```bash
cd llm-data-quality
python -m http.server 8000
# 打开 http://localhost:8000
```

## 部署 GitHub Pages

仓库需为**公开**（免费账号的私有仓库不支持 Pages）。
Settings → Pages → Source 选 `main` 分支根目录，保存后访问
`https://<你的用户名>.github.io/<仓库名>/`。
