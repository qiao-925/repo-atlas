# Repo Atlas

> 一个为 GitHub 账号生成静态分析看板的工具。

Repo Atlas 通过脚本分析单个 GitHub 账号下的所有仓库，快速生成一个自包含的 HTML 看板，用于：

- **看清全局**：展示所有仓库的活跃度、聚类和核心资产。
- **识别混乱**：找出久未更新、可归档或可删除的仓库。
- **指导行动**：提供清理和优化的建议。

它是一个轻量级的诊断工具，而不是一个重型的工程化项目。

## 核心功能 (v1)

- 拉取 GitHub 账号所有仓库的元数据。
- 生成一个包含以下内容的静态 `dashboard.html`：
  - **全局仪表盘**：仓库总数、活跃度分布、语言分布。
  - **仓库地图**：按主题聚类（例如 Assemble 流水线、研究型 Agent、基础设施等）。
  - **行动建议**：识别可归档或需要关注的仓库。

## 如何使用

```bash
# 1. 拉取最新的仓库数据
python scripts/fetch_repos.py

# 2. 分析数据并生成报告
python scripts/analyze_portfolio.py

# 3. 渲染最终的 HTML 看板
python scripts/render_reports.py

# 4. 在浏览器中打开 dashboard.html
```

## 项目结构

```text
repo-atlas/
├─ README.md
├─ docs
│  └─ architecture.md  # 原始架构设计（仅供参考）
├─ scripts/             # 核心脚本
├─ data/                # 生成的数据和报告
│  ├─ raw/             # 原始数据
│  └─ derived/         # 分析后的数据
└─ dashboard.html       # 最终产出
```
