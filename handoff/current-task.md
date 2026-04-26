# 当前任务：Repo Atlas 项目来源质量控制优化交接

## 目标

- 为 `repo-atlas` 的 Windsurf → Cursor 协作链做一轮**轻量级来源质量优化**：让 `/handoff`、`/review` 和 Cursor prompt 模板更明确地依赖权威上下文、区分事实与推断、在证据不足时降低结论力度，同时**保持现有 relay + state 机制不变**。
- 这次交接不是新增 relay 功能，也不是继续旧的脚本可读性重构。目标是让后续 handoff / review 更稳地以“当前代码、状态文件、实际 diff”为准，而不是被会话记忆或背景材料带偏。

## 已确认约束

- AGENTS.md:3-5
  - 保持轻量，不项目化。
  - 输出风格简洁，不要把流程文档写成研究报告。
- AGENTS.md:9-13
  - 先充分调研，再改代码或 workflow。
  - 跨工具协作优先通过文件中转。
  - `computer use` 只负责粘贴和触发，不负责思考型传输。
- AGENTS.md:31-35
  - 修改后必须做自检。
  - 若自检发现问题，最多三轮自修复。
- `source-quality-control`
  - 这轮要先读取这个 skill。
  - 只吸收与“来源分级、结论力度、事实/推断区分、输出可复查”直接相关的规则。
  - 不把它扩展成大而全的研究模板。

## 当前真实协作链路

### handoff workflow

- `.windsurf/workflows/handoff.md:5-47`
  - 已定义：读取上下文、调研代码、写 `handoff/current-task.md` 与 `handoff/cursor-prompt.md`、relay、等待态、自动检测 `review_ready`、进入 review。
  - 当前缺口：虽已强调“以文件和代码为准”，但还没有显式写出来源优先级、证据强弱和“事实 / 推断 / 待确认项”的区分。

### review workflow

- `.windsurf/workflows/review.md:5-23`
  - 已定义：读取 current-task / state / diff，只围绕 handoff 目标 review，并在结束后写 `reviewed`。
  - 当前缺口：还没有明确要求“只报告高置信问题”“证据不足时降级结论”“把缺少验证和真实 bug 区分开”。

### prompt template

- `prompts/cursor-task-template.md:1-20`
  - 当前模板很轻，但偏薄。
  - 已有 `Task / Context / What to change / Expected result / Do NOT`。
  - 当前缺口：缺少“source of truth / stable boundary / validation / unknowns”这类轻量结构，导致交接 prompt 容易只靠文字组织，不够抗偏差。

### 现有 stable 行为

- `scripts/relay_to_cursor.py:154-183`
  - relay 的真实职责已经很明确：检查窗口、粘贴、可选发送、调用状态脚本写入 `awaiting_cursor`。
- `scripts/handoff_state.py:120-175`
  - 状态机已支持 `awaiting_cursor / review_ready / reviewed`。
  - 这轮默认不要改状态语义，也不要重写 target file / fingerprint 机制。

## 优先级与问题定位

### 第一优先级：`.windsurf/workflows/handoff.md`

- 文件范围：`.windsurf/workflows/handoff.md:5-47`
- 关键观察：
  - 当前 workflow 已有“当前代码与 handoff 文件优先”的方向，但没有显式来源分级。
  - 如果要落实 `source-quality-control`，最应该先补的是：哪些是 P0 权威来源、哪些只能当补充、证据不足时要怎么写。
  - 还要保持现有 relay / waiting / review-ready 链路原样可用。
- 建议方向：
  - 加入面向这个仓库的 P0 / P1 / P2 来源层级。
  - 要求 handoff 输出简短区分：已确认事实、基于代码的推断、待确认项。
  - 明确“真实代码 / state / diff 高于会话记忆和旧总结”。

### 第二优先级：`.windsurf/workflows/review.md`

- 文件范围：`.windsurf/workflows/review.md:5-23`
- 关键观察：
  - 当前 review 目标已经对，但还可以更明确地限定“只报高置信问题”。
  - 对“自检缺失”“状态未更新”“证据不足”这类情况，应该写成缺口或风险，不应伪装成已确认 bug。
  - 最终结论格式和 `mark-reviewed` 行为是现有协作契约，不能破坏。
- 建议方向：
  - 增加证据优先级和结论力度要求。
  - 显式区分：确认违反约束 / 缺少验证证据 / 需要人工确认的低置信风险。

### 第三优先级：`prompts/cursor-task-template.md`

- 文件范围：`prompts/cursor-task-template.md:1-20`
- 关键观察：
  - 模板足够简洁，但对“source of truth / stable boundary / validation / unknowns”承载不足。
  - 这会让 handoff 文本容易含混，尤其是当任务涉及状态机、工作流约束或多类上下文来源时。
- 建议方向：
  - 在不显著加重模板的前提下，补齐最小必要结构。
  - 保持 Cursor 可执行，不要把模板变成长文档生产器。

## 推荐改造方式

### 对 `handoff.md`

目标是让 handoff 步骤能明确回答：这次交接基于哪些权威材料、哪些只是补充、哪里仍然有未知项。

建议优先补充：

- 先读取 `source-quality-control` skill，再做 handoff 研究。
- 针对这个仓库明确来源分级：
  - P0：当前仓库代码、workflow/template、handoff 文件、状态文件、实际 diff、实际命令输出。
  - P1：AGENTS.md、repo 内说明文档、CHANGELOG。
  - P2：会话记忆、历史总结、背景性材料。
- 明确要求：P0 与 P1 / P2 冲突时，以 P0 为准。
- 交接输出里简短区分“事实 / 推断 / 待确认项”，但不要写成长报告。
- relay、等待态、自动进入 review 的现有步骤保留。

### 对 `review.md`

目标是让 review 更严格地基于证据，而不是基于感觉补全。

建议优先补充：

- 先看 state、target files、changed files 和真实 diff，再下判断。
- 只报告高置信问题。
- 把“确认违反约束”与“缺少验证证据”拆开写。
- 若只有弱证据，降低结论力度，不要强判。
- 保持现有最终结论格式和写 `reviewed` 的动作不变。

### 对 `cursor-task-template.md`

目标是让模板仍然轻量，但更适合质量可控的 handoff。

建议优先补充：

- `Source of truth / Stable boundaries` 这类轻量结构。
- `Validation` 或等价的自检要求占位。
- 必要时给出 `Unknowns / Open questions`，避免把猜测写成事实。

要求：

- 保持模板短小、可执行。
- 不要把它扩展成调研报告模板。
- `What to change` 仍要保持逐条可执行。

## 稳定区域 / 不应修改

- `scripts/relay_to_cursor.py:154-183`
  - 默认不要改；除非 workflow 文案无法如实描述当前实现。
- `scripts/handoff_state.py:120-175`
  - 默认不要改；`awaiting_cursor / review_ready / reviewed` 语义保持不变。
- `handoff/current-task.md` 与 `handoff/cursor-prompt.md`
  - 这是本轮交接产物，不是让 Cursor 再去重构的目标。
- 不新增依赖，不引入新的状态文件格式，不改 relay 的职责边界。

## 自检要求

按这轮任务做最小必要验证：

1. 重新读取修改后的 `.windsurf/workflows/handoff.md`、`.windsurf/workflows/review.md`、`prompts/cursor-task-template.md`
2. 确认来源优先级已明确，且当前代码 / 状态 / diff 明确高于会话记忆与背景材料
3. 确认 review 只要求报告高置信问题，并能区分“缺少证据”和“确认出错”
4. 确认 relay / waiting / review-ready / reviewed 这些现有步骤没有被删改坏
5. 确认模板仍然轻量、可执行，没有变成长篇调研模板

## 风险提醒

- 最容易做坏的是把 workflow / template 写得过重，导致实际使用时噪音上升。
- 第二个风险是把“来源质量控制”理解成“必须堆很多引用”，从而破坏轻量 handoff。
- 第三个风险是顺手改 Python 脚本行为，导致 workflow 文案和真实 relay / state 逻辑发生偏移。
