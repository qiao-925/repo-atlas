## 偏好

- 保持轻量，不项目化
- 输出风格偏简洁，不要长篇大论和说教感
- 不需要反复确认，直接做

## 执行原则

- 执行前先做充分调研，不要拼手感
- 数据始终实时读取，不做本地存档/缓存（保证数据时效性）
- 聚类规则（CLUSTER_RULES）如有变化，需同步更新文档说明
- 若采用 Windsurf → Cursor 协作流，`computer use` 只负责粘贴和触发，不负责思考型传输、临场总结或跨工具重建上下文
- 跨工具协作优先通过文件中转（如 plan/review/fixlist），不要把 GUI 自动化作为主编排层

## 技术栈

- **语言**：Python 3.x
- **依赖**：GitHub CLI (gh) 用于拉取仓库数据
- **输出**：静态 HTML 看板

## 项目结构

```
repo-atlas/
├─ scripts/        # 核心脚本（fetch, analyze, render）
├─ data/           # 数据目录（raw/ 原始数据, derived/ 分析结果）
├─ web/            # Next.js 前端（可选）
└─ dashboard.html  # 静态看板输出
```

## 自检规则

- **修改后必须自检**：对脚本修改后，运行完整流程验证实际效果
- **自检流程**：`fetch_repos.py → analyze_portfolio.py → render_reports.py → 打开 dashboard.html`
- **最多三轮自修复**：若自检发现异常，先修复，最多尝试三轮，最后提交给人类 review