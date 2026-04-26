# CHANGELOG

## 2026-04-24

- **增加完成回执要求**：更新当前 `handoff/cursor-prompt.md`，要求 Cursor 在完成改动并通过自检后执行 `python3 scripts/handoff_state.py detect`，显式将 `handoff/state.json` 切到 `review_ready`。
- **增加 handoff 状态机**：新增 `scripts/handoff_state.py`，并让 relay 与 workflow 使用 `handoff/state.json` 自动识别 Cursor 改动是否已进入 review-ready。
- **优化 Windsurf-Cursor 协作工作流**：增强 `.windsurf/workflows/handoff.md` 的 relay、等待态与 review 回流步骤，并新增 repo-atlas 本地 `.windsurf/workflows/review.md`。
- **新增 Cursor relay 脚本**：添加 `scripts/relay_to_cursor.py`，支持检查 handoff 文件、定位 Cursor 窗口并执行粘贴中继。
- **完成 relay 实测**：已成功将 `handoff/cursor-prompt.md` 粘贴到当前 Cursor 窗口，未自动发送。
