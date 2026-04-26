## Task
对 `repo-atlas` 的 Windsurf → Cursor 协作链做一轮轻量级来源质量优化：更新 `/.windsurf/workflows/handoff.md`、`/.windsurf/workflows/review.md` 和 `prompts/cursor-task-template.md`，让后续 handoff / review 更明确地以权威来源为准，并在证据不足时降低结论力度，同时**保持现有 relay + state 行为不变**。

## Context
- 目标 workflow：`.windsurf/workflows/handoff.md:5-47`
  - 已有读取上下文、调研代码、写 handoff 文件、relay、等待态、自动进入 review 的链路。
  - 当前缺口：没有显式来源分级，也没有把“事实 / 推断 / 待确认项”说清楚。
- 目标 review：`.windsurf/workflows/review.md:5-23`
  - 已有 current-task / state / diff 驱动的 review 结构。
  - 当前缺口：缺少“只报高置信问题”“证据不足时降级结论”“缺少验证证据 != 已确认 bug”的明确规则。
- 目标模板：`prompts/cursor-task-template.md:1-20`
  - 当前模板足够轻，但对 `source of truth`、稳定边界、验证要求、未知项承载不足。
- 项目约束：AGENTS.md:3-5, 9-13, 31-35
  - 保持轻量，不项目化。
  - 先充分调研，再改 workflow / template。
  - 跨工具协作优先通过文件中转。
  - 修改后必须自检。
- 稳定实现：scripts/relay_to_cursor.py:154-183, scripts/handoff_state.py:120-175
  - relay 已负责检查窗口、粘贴、可选发送、写入 `awaiting_cursor`。
  - state 已支持 `awaiting_cursor / review_ready / reviewed`。
  - 这轮优先对齐文案，不改现有行为。

## What to change
1. 先读取 skill `source-quality-control`。只吸收与以下内容直接相关的规则：
   - 来源分级（P0 / P1 / P2）
   - 事实 / 推断 / 建议区分
   - 证据强度与结论力度校准
   - 输出可复查
   不要把 workflow 或模板改造成大而全的研究文档。
2. 更新 `.windsurf/workflows/handoff.md`，把来源质量控制落到当前协作流里。至少补齐这些点：
   - 这个仓库里的 P0 / P1 / P2 来源层级
   - 当来源冲突时，以 P0 为准
   - handoff 研究和交接内容需要简短区分：已确认事实、基于代码的推断、待确认项
   - 等待态期间继续以 handoff 文件、state、实际代码和 diff 为准，不回退到会话记忆
   - 现有 relay / awaiting / review-ready 流程保留
3. 更新 `.windsurf/workflows/review.md`，让 review 的结论力度更受证据约束。至少补齐这些点：
   - 先读 state 的 `target_files`、`changed_files`、`status`，再结合实际 diff 判断
   - 只报告高置信问题
   - 明确区分：确认违反约束 / 缺少验证证据 / 低置信风险待人工确认
   - 若只有弱证据，降低结论力度，不要强判
   - 保持最终结论格式和 `reviewed` 状态更新动作不变
4. 更新 `prompts/cursor-task-template.md`，让模板在保持轻量的前提下，最少支持这些结构中的等价表达：
   - `Source of truth` 或权威上下文来源
   - `Stable boundaries` 或不该动的稳定区
   - `Validation` 或自检要求
   - `Unknowns / Open questions`，避免把猜测写成事实
   同时保持：
   - `Context` 仍要求精确文件路径和行号（使用 repo 相对路径）
   - `What to change` 仍是逐条可执行动作
   - 模板整体仍然短小
5. 如果 workflow / template 文案与当前 relay / state 脚本行为不一致，优先让文案对齐当前实现；不要顺手扩展 relay 职责，也不要改状态机语义。
6. 完成修改后做最小必要自检：
   - 重新读取修改后的 `.windsurf/workflows/handoff.md`
   - 重新读取修改后的 `.windsurf/workflows/review.md`
   - 重新读取修改后的 `prompts/cursor-task-template.md`
   - 确认来源优先级明确、事实/推断/待确认项可区分、relay/state 链路未被破坏、模板仍轻量可执行
7. 完成改动并确认自检通过后，执行 `python3 scripts/handoff_state.py detect`，让 `handoff/state.json` 从 `awaiting_cursor` 更新为 `review_ready`。要求：
   - 只有在本轮目标文件已实际改动后才执行
   - 执行后确认 `status` 为 `review_ready`
   - 不要把状态写成 `reviewed`

## Expected result
- `.windsurf/workflows/handoff.md` 更明确地说明：哪些是权威来源、哪些只是补充来源，以及证据不足时该如何写
- `.windsurf/workflows/review.md` 更明确地以 state + diff + 自检证据为准，并限制只报高置信问题
- `prompts/cursor-task-template.md` 仍然轻量，但更能承载高质量 handoff
- 现有 relay、等待态、`awaiting_cursor / review_ready / reviewed` 生命周期不变
- 完成最小必要自检
- `handoff/state.json` 在完成后被更新为 `review_ready`

## Do NOT
- 不要修改 `scripts/handoff_state.py:120-175` 的状态语义，除非文案无法如实对齐当前实现
- 不要修改 `scripts/relay_to_cursor.py:154-183` 的职责边界，除非文案无法如实对齐当前实现
- 不要新增依赖
- 不要把 workflow / template 扩写成长篇调研模板或制度文档
- 不要把会话记忆、历史总结、背景资料写成比当前代码 / state / diff 更高优先级
- 不要顺手重构无关 Python 脚本、前端页面或部署流程
